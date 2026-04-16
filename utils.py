

EVAL_IMAGE_PROMPT = '''
You are an expert image editing evaluation model. You will evaluate the quality of an edited image compared to the original image.

**Input Information:**
- Original Prompt: {original_prompt}
- Edited Prompt: {edited_prompt}
- Original Image: [First image]
- Edited Image: [Second image]

**Evaluation Task:**
Evaluate the edited image across the following three dimensions. For each dimension, provide a score from 0 to 5:
- 0: Completely fails the criterion
- 1: Poor quality with major issues
- 2: Below average with noticeable problems
- 3: Acceptable quality with minor issues
- 4: Good quality with very minor flaws
- 5: Excellent quality, meets all requirements

**Evaluation Dimensions:**

1. **Structural Fidelity (structural_fidelity)**: Focus on the consistency of entities in the edited image compared to the original.
   Evaluate whether the structure, pose, orientation, and spatial relationships of objects/subjects remain consistent with the original image.
   Unedited entities should maintain their original structure, action, and direction. Score 5 if entity consistency is perfectly preserved, score 0 if completely inconsistent.

2. **Text-Image Alignment (text_image_alignment)**: How well does the edited image match the edited prompt?
   The edited content should accurately reflect the requested changes described in the edited prompt. Score 5 for perfect alignment, score 0 for no alignment.

3. **Background Consistency (background_consistency)**: Evaluate the consistency of all regions EXCEPT the edited subject/object.
   The background and all unedited parts should remain identical to the original image. Check for unwanted changes, color shifts, or distortions
   in areas that should not be modified. Score 5 for perfect consistency of non-edited regions, score 0 for major inconsistencies.

4. **Naturalness (naturalness)**: Evaluate whether the overall scene in the edited image appears natural.
    Look for noticeable flaws—such as inconsistent lighting, perspective errors, structural distortions, or watermarks—that break the sense of realism. 
    Score 5 if the image looks completely natural; score 0 for severe unnaturalness.

**Important Guidelines:**
- Be critical and use the full range of scores (0-5). Avoid clustering all scores around 3-4.
- Different images will have different quality levels - some edits are inherently harder than others.
- A perfect score (5) should be rare and reserved for truly excellent results.
- Scores below 2 should be given when there are significant failures.
- Consider the difficulty of the edit when scoring, but maintain consistent standards.

**Output Format:**
Provide your evaluation in the following JSON format:
```json
{{
  "structural_fidelity": <score>,
  "text_image_alignment": <score>,
  "background_consistency": <score>,
  "naturalness": <score>,
  "explanation": {{
    "structural_fidelity": "<brief explanation>",
    "text_image_alignment": "<brief explanation>",
    "background_consistency": "<brief explanation>",
    "naturalness": "<brief explanation>"
  }}
}}
```

Now evaluate the images and provide your scores in the JSON format above.
'''

EVAL_VIDEO_PROMPT = '''
You are an expert video editing evaluation model. You will evaluate the quality of an edited video compared to the original video.

**Input Information:**
- Original Prompt: {original_prompt}
- Edited Prompt: {edited_prompt}
- Original Video: [First video]
- Edited Video: [Second video]

**Evaluation Task:**
Evaluate the edited video across the following five dimensions. For each dimension, provide a score from 0 to 5:
- 0: Completely fails the criterion
- 1: Poor quality with major issues
- 2: Below average with noticeable problems
- 3: Acceptable quality with minor issues
- 4: Good quality with very minor flaws
- 5: Excellent quality, meets all requirements

**Evaluation Dimensions:**

1. **Structural Fidelity (structural_fidelity)**: Focus on the consistency of entities in the edited video compared to the original.
   Evaluate whether the structure, pose, orientation, and spatial relationships of objects/subjects remain consistent with the original video.
   Unedited entities should maintain their original structure, action, and direction. Score 5 if entity consistency is perfectly preserved, score 0 if completely inconsistent.

2. **Text-video Alignment (text_video_alignment)**: How well does the edited video match the edited prompt?
   The edited content should accurately reflect the requested changes described in the edited prompt. Score 5 for perfect alignment, score 0 for no alignment.

3. **Background Consistency (background_consistency)**: Evaluate the consistency of all regions EXCEPT the edited subject/object.
   The background and all unedited parts should remain identical to the original video. Check for unwanted changes, color shifts, or distortions
   in areas that should not be modified. Score 5 for perfect consistency of non-edited regions, score 0 for major inconsistencies.

4. **Naturalness (naturalness)**: Evaluate whether the overall scene in the edited video appears natural.
    Look for noticeable flaws—such as inconsistent lighting, perspective errors, structural distortions, or watermarks—that break the sense of realism. 
    Score 5 if the video looks completely natural; score 0 for severe unnaturalness.

5. **Temporal-Spatial Consistency (temporal_spatial_consistency)**: Focus on the continuity and logical flow of the video/sequence across time and space.
    Evaluate whether objects maintain their identity, motion trajectories are fluid, and spatial logic (like gravity or depth) remains coherent throughout the duration of the edit. 
    Ensure that changes do not cause "flickering," sudden teleportation of objects, or logical breaks in the environment's physics. 
    Score 5 if the motion and spatial logic are perfectly seamless; score 0 for chaotic or physically impossible transitions.

**Important Guidelines:**
- Be critical and use the full range of scores (0-5). Avoid clustering all scores around 3-4.
- Different videos will have different quality levels - some edits are inherently harder than others.
- A perfect score (5) should be rare and reserved for truly excellent results.
- Scores below 2 should be given when there are significant failures.
- Consider the difficulty of the edit when scoring, but maintain consistent standards.

**Output Format:**
Provide your evaluation in the following JSON format:
```json
{{
  "structural_fidelity": <score>,
  "text_video_alignment": <score>,
  "background_consistency": <score>,
  "naturalness": <score>,
  "temporal_spatial_consistency": <score>,
  "explanation": {{
    "structural_fidelity": "<brief explanation>",
    "text_video_alignment": "<brief explanation>",
    "background_consistency": "<brief explanation>",
    "naturalness": "<brief explanation>",
    "temporal_spatial_consistency": "<brief explanation>"
  }}
}}
```

Now evaluate the videos and provide your scores in the JSON format above.
'''

IMAGE_SCORE_KEYS = [
    "structural_fidelity",
    "text_image_alignment",
    "background_consistency",
    "naturalness",
]

VIDEO_SCORE_KEYS = [
    "structural_fidelity",
    "text_video_alignment",
    "background_consistency",
    "naturalness",
    "temporal_spatial_consistency",
]