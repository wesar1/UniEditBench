import os
import concurrent
import concurrent.futures
import json
from openai import OpenAI
from tqdm import tqdm

from utils import EVAL_IMAGE_PROMPT, EVAL_VIDEO_PROMPT


class QwenVLAPI:
    def __init__(self, port: int = 8003, api_key: str = 'EMPTY'):
        base_url = f'http://127.0.0.1:{port}/v1'
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.models = [model.id for model in self.client.models.list().data]
        print(f"VLLM Models: {self.models}")

    def _infer_media_type(self, item: dict) -> str:
        path = item.get('path', '')
        if path.endswith('.mp4'):
            return 'video'
        if path.endswith('.png'):
            return 'image'
        raise ValueError(f"Cannot infer media type from 'path' extension: {path}")

    def eval_one(self, item: dict, media_type: str | None = None):
        """
        Run inference evaluation on a single sample.

        Expected item format:
          {path, edit_path, source_prompt, target_prompt}
          path ends with .png for image, .mp4 for video.

        After inference, 'prompt' and 'response' will be written into item.
        """
        if media_type is None:
            media_type = self._infer_media_type(item)

        prompt_data = {
            'source_prompt': item['source_prompt'],
            'target_prompt': item['target_prompt'],
        }

        source_path = item['path']
        edited_path = item['edit_path']
        if media_type == 'image':
            prompt_text = EVAL_IMAGE_PROMPT.format(**prompt_data)
        else:
            prompt_text = EVAL_VIDEO_PROMPT.format(**prompt_data)

        content = [
            {'type': media_type, media_type: source_path},
            {'type': media_type, media_type: edited_path},
            {'type': 'text', 'text': prompt_text},
        ]
        messages = [{'role': 'user', 'content': content}]

        resp = self.client.chat.completions.create(
            model=self.models[0],
            messages=messages,
            max_tokens=2048,
            temperature=0,
        )
        res = resp.choices[0].message.content
        item.update({'prompt': prompt_text, 'response': res})

    def eval_batch(
        self,
        metadata_path: str,
        save_path: str,
        media_type: str | None = None,
        max_workers: int = 10,
    ):
        """
        Batch inference evaluation.

        Args:
            metadata_path: Path to the input metadata JSON file.
            save_path: Path to save the results.
            media_type: 'image' or 'video'. Auto-inferred if None.
            max_workers: Number of concurrent threads.
        """
        save_dir = os.path.dirname(save_path)
        if save_dir and not os.path.exists(save_dir):
            os.makedirs(save_dir, exist_ok=True)

        with open(metadata_path, 'r', encoding='utf-8') as f:
            metadata_list = json.load(f)

        def _process(item):
            self.eval_one(item, media_type=media_type)

        _run_parallel(
            item_list=metadata_list,
            max_workers=max_workers,
            process_one=_process,
            desc=f"'{self.models[0]}' inferencing",
        )

        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(metadata_list, f, indent=2, ensure_ascii=False)

        return metadata_list


def _run_parallel(item_list: list[dict], max_workers: int, process_one, desc: str):
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(process_one, item) for item in item_list]
        pbar = tqdm(total=len(futures), desc=desc)
        error_messages = []
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as e:
                error_messages.append(str(e))
            pbar.update(1)
        pbar.close()

    if error_messages:
        print(f"{len(error_messages)} task(s) failed:")
        for err in error_messages:
            print(err)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="Image/Video editing quality evaluation inference")
    parser.add_argument('--metadata_path', type=str, required=True)
    parser.add_argument('--save_path', type=str, required=True)
    parser.add_argument('--media_type', type=str, default=None, choices=['image', 'video'])
    parser.add_argument('--port', type=int, default=8003)
    parser.add_argument('--max_workers', type=int, default=10)
    args = parser.parse_args()

    evaluator = QwenVLAPI(port=args.port)
    evaluator.eval_batch(
        metadata_path=args.metadata_path,
        save_path=args.save_path,
        media_type=args.media_type,
        max_workers=args.max_workers,
    )
