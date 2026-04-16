# image inference
python inference.py \
    --metadata_path path_tor_your_metadata.json \
    --save_path ./results/image_eval.json \
    --media_type image \
    --port 8003 \
    --max_workers 10

# video inference
python inference.py \
    --metadata_path path_tor_your_metadata.json \
    --save_path ./results/video_eval.json \
    --media_type video \
    --port 8004 \
    --max_workers 10