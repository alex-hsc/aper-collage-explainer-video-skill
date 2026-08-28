# High-detail visual standard

## Contents

- Shot contract
- Asset density
- Prompt contract
- Continuity
- Contact-sheet gate
- Motion fallback

## Shot contract

Make every shot readable as a concrete event in a specific place. Include:

1. one primary subject;
2. one narration-relevant environment;
3. one visible mechanism or causal action;
4. one visible result;
5. supporting objects that strengthen scale, location or comparison.

Do not treat a colored background, texture, shadow, repeated particle, arrowhead or subtitle as a concrete asset.

## Asset density

- Require 5–12 concrete recognizable assets per shot.
- Keep 3–6 large animated groups so motion remains controllable.
- Prefer fewer strong assets over decorative clutter, but never approve a finished scene made only from circles, lines and generic icons.
- Use at least three composition families across a 60-second video and at least five across a 90-second video: environmental wide, character observation, experiment/cutaway, mechanism close-up, comparison/split scene, consequence, recap.
- Give adjacent shots different `unique_composition_key` values.

## Prompt contract

For each ImageGen prompt specify:

```text
Use case: scientific-educational
Asset type: 16:9 explainer-video end frame
Scene/backdrop: <specific place and time>
Primary subjects: <recognizable people/objects>
Mechanism: <visible scientific action and direction>
Supporting assets: <3–8 specific props or landmarks>
Style: premium handcrafted dimensional paper diorama
Composition: <shot size, spatial hierarchy, subtitle-safe area>
Continuity: <recurring character/vehicle/palette>
Constraints: no text, numbers, logos, UI, watermark or malformed objects
Avoid: sparse geometry, generic icons, decorative clutter, repeated template composition
```

Use one prompt per distinct shot. Persist selected project images under `visual/end-frames/` and record the final prompt set.

## Continuity

Lock recurring identity traits before generating the pilot: character age/clothing, vehicle color/type, tool shapes, landmark palette, paper material and semantic colors. Reuse approved images as references when the image tool supports them.

Continuity does not mean repeating one layout. Keep identity stable while changing camera distance, setting, action and explanatory mechanism.

## Contact-sheet gate

Build a contact sheet with one representative frame per shot. Fail the visual layer if any condition holds:

- a shot has fewer than five meaningful concrete assets;
- two adjacent shots reuse the same layout with only noun or color substitution;
- the mechanism is not understandable without subtitles;
- generated text, logos, watermarks, broken anatomy or malformed vehicles appear;
- subtitles cover the primary subject or mechanism;
- decorative richness makes the causal action hard to find.

Record the review in `qa/gate-2.md` and the asset inventory in `visual/asset-manifest.json`.

## Motion fallback

Prefer approved start/end keyframe motion. Reject generated motion that adds objects, deforms vehicles or bodies, drifts the camera, creates text or carries an audio track.

When a provider trial fails and the user has authorized a local fallback, use restrained deterministic paper reveals or no more than 2.5% depth motion. Record the rejected trial and accepted deviation in `qa/motion.json` and `qa/final.md`; never present the rejected model output as the final shot.
