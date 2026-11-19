import json, os, subprocess, tempfile, textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output"
WORK = Path(tempfile.mkdtemp(prefix="unknown-files-"))
FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf"
]
FONT_REG = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf"
]

def font(size, bold=False):
    candidates = FONT_CANDIDATES if bold else FONT_REG
    for path in candidates:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()

def wrap(draw, text, fnt, max_width):
    words, lines, line = text.split(), [], ""
    for word in words:
        trial = (line + " " + word).strip()
        if draw.textbbox((0, 0), trial, font=fnt)[2] <= max_width:
            line = trial
        else:
            if line: lines.append(line)
            line = word
    if line: lines.append(line)
    return lines

def make_frame(path, heading, narration, width, height, index, total):
    im = Image.new("RGB", (width, height))
    px = im.load()
    for y in range(height):
        for x in range(width):
            glow = max(0, 1 - (((x-width*.72)/(width*.9))**2 + ((y-height*.42)/(height*.9))**2)**.5)
            px[x,y] = (int(3+5*glow), int(8+20*glow), int(20+36*glow))
    d = ImageDraw.Draw(im)
    margin = int(width*.085)
    accent = (62, 177, 255)
    d.rounded_rectangle((margin, int(height*.12), margin+10, int(height*.12)+int(height*.12)), radius=5, fill=accent)
    small = font(max(18, int(width*.018)))
    head = font(max(34, int(width*.052)), True)
    body = font(max(25, int(width*.029)))
    d.text((margin, int(height*.08)), "THE UNKNOWN FILES  /  BEYOND WHAT WE KNOW", font=small, fill=(145,190,225))
    y = int(height*.31)
    for line in wrap(d, heading.upper(), head, width-2*margin):
        d.text((margin, y), line, font=head, fill=(245,249,255), stroke_width=1, stroke_fill=(10,20,35))
        y += int(head.size*1.25)
    y += int(height*.045)
    for line in wrap(d, narration, body, width-2*margin):
        d.text((margin, y), line, font=body, fill=(205,220,238))
        y += int(body.size*1.55)
    d.text((margin, height-int(height*.09)), f"FILE {index:02d}  •  {index}/{total}", font=small, fill=accent)
    im.save(path, quality=94)

def run(cmd):
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def build_video(item, filename, width, height, speed, voice):
    scenes = item["scenes"]
    parts = []
    for i, scene in enumerate(scenes, 1):
        image_path = WORK / f"{filename}-{i}.jpg"
        audio_path = WORK / f"{filename}-{i}.wav"
        clip_path = WORK / f"{filename}-{i}.mp4"
        make_frame(image_path, scene["heading"], scene["text"], width, height, i, len(scenes))
        narration = scene["heading"] + ". " + scene["text"]
        subprocess.run(["espeak-ng", "-v", voice, "-s", str(speed), "-w", str(audio_path), narration], check=True)
        run(["ffmpeg", "-y", "-loop", "1", "-i", str(image_path), "-i", str(audio_path),
             "-c:v", "libx264", "-tune", "stillimage", "-c:a", "aac", "-b:a", "128k",
             "-pix_fmt", "yuv420p", "-shortest", "-vf", f"scale={width}:{height},format=yuv420p",
             "-movflags", "+faststart", str(clip_path)])
        parts.append(clip_path)
    concat = WORK / f"{filename}-concat.txt"
    concat.write_text("".join(f"file '{p.as_posix()}'\n" for p in parts), encoding="utf-8")
    OUT.mkdir(exist_ok=True)
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat), "-c", "copy",
         "-movflags", "+faststart", str(OUT / filename)])

def main():
    data = json.loads((ROOT / "content/episode.json").read_text(encoding="utf-8"))
    build_video(data["long"], "black-hole-long.mp4", 1920, 1080, 148, "en-us")
    for i, short in enumerate(data["shorts"], 1):
        build_video(short, f"black-hole-short-{i}.mp4", 1080, 1920, 165, "en-us")
    (OUT / "metadata.txt").write_text(
        "LONG VIDEO\nTitle: " + data["long"]["title"] + "\nDescription: " + data["long"]["description"] +
        "\n\nSHORTS\n" + "\n".join(s["title"] + "\n" + s["description"] for s in data["shorts"]),
        encoding="utf-8")
    print("Rendered 1 long video and 2 Shorts in output/")

if __name__ == "__main__":
    main()
