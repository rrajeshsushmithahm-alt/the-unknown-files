# THE UNKNOWN FILES

Free, open-source video rendering workflow for the faceless educational channel **THE UNKNOWN FILES**.

## What this repository currently does

- Runs in GitHub Actions every Monday at 18:00 India Standard Time (12:30 UTC).
- Can also be started manually from the Actions tab.
- Uses FFmpeg, eSpeak NG and Pillow to render one 16:9 long video and two 9:16 Shorts from `content/episode.json`.
- Saves MP4 files and metadata as a downloadable workflow artifact for 14 days.
- Requires no paid APIs, subscriptions, API keys or local computer while the cloud job runs.

## Important limitations

This first version renders the episode scripts already stored in the repository. It does **not** independently research the internet, write new scripts, or publish to YouTube. The weekly script-pack reminder in ChatGPT is a separate workflow. The rendered voice is synthetic and the visuals are original text-led graphics, not stock footage.

YouTube upload automation is not enabled yet. It requires a secure one-time Google/YouTube OAuth setup and storing credentials in GitHub Actions Secrets. Never commit credentials or paste access tokens into chat.

GitHub Actions usage is subject to GitHub's current plan limits and fair-use rules. Scheduled runs can be delayed, and free cloud execution is not an unlimited hosting guarantee.

## Run manually

1. Open the repository's **Actions** tab.
2. Select **Render THE UNKNOWN FILES videos**.
3. Select **Run workflow**.
4. When it finishes, open the run and download the `the-unknown-files-videos` artifact.

## Update the episode

Edit `content/episode.json` with original scripts you have rights to use. Keep the `long.scenes` and `shorts[].scenes` structure. Do not upload copied scripts or third-party video/audio without permission or a suitable license.

## Files

- `content/episode.json`: first black-hole episode and two Shorts.
- `scripts/render.py`: offline renderer.
- `.github/workflows/render.yml`: weekly and manual cloud workflow.
