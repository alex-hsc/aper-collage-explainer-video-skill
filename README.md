# Paper Collage Explainer Video Skill

一个面向 Codex 的开源技能，用模块化、可返工的工作流制作纸拼贴 / Vox 风格科普讲解视频。

它覆盖选题研究、事实脚本、分镜、视觉隐喻、高细节形象素材、统一关键帧、首尾帧动画、自然童声旁白、标点安全字幕、FFmpeg 合成和逐镜 QA。每个中间产物都会保留，因此某一镜失败时无需重做整条视频。

## 特性

- 五层流水线：导演、视觉、动态、音频、合成
- 每镜 3–6 个可动画纸片组，并要求 5–12 个与知识点有关的具体可辨认素材
- `visual/asset-manifest.json` 记录人物、环境、机制、辅助素材与独立构图
- 默认拒绝单一几何符号、空背景、通用图标和重复模板构图
- 一镜一条 ImageGen 高细节提示词，固定角色、车辆、器材和视觉语义
- 全镜头联系表是强制质量门，自动检查最低素材密度与相邻镜头构图重复
- 默认锁定镜头，以首帧和末帧约束纸片的滑入、弹出、展开和堆叠
- 中文少儿科普默认采用 `zh-CN-XiaoyiNeural`，不使用操作系统自带人声
- 旁白实测时长作为主时钟，画面适配声音而不是反过来
- 字幕自动换行时，逗号、句号、问号等标点保留在上一行
- 项目清单、分镜、关键帧、动作提示词、时间轴和 QA 记录均可独立返工

## 安装

```bash
git clone https://github.com/alex-hsc/aper-collage-explainer-video-skill.git
mkdir -p ~/.codex/skills
cp -R paper-collage-explainer-video-skill/paper-collage-explainer-video ~/.codex/skills/
```

重新启动 Codex，或让 Codex 重新扫描技能目录。之后可这样调用：

```text
使用 $paper-collage-explainer-video 制作一条适合小学生的横屏纸拼贴科普动画，
主题是“彩虹是怎么形成的”，每镜使用 5–12 个形象具体的素材，
配图丰富，构图不能重复，字幕换行后不能以标点开头。
```

## 依赖

核心脚本使用 Python 3 标准库。根据所选工作流，还需要：

- FFmpeg / ffprobe：音频规范化、时间测量和最终合成
- `edge-tts`：在线生成 `zh-CN-XiaoyiNeural` 中文旁白
- 可用的图像生成工具：生成和编辑纸拼贴关键帧
- Node.js、`npx`、`agnes-ai-cli` 和 Agnes API key：可选，用于首尾帧动态生成

Agnes keyframe 上传和在线 TTS 都是外部网络操作。技能会要求先获得用户授权，并只从环境变量读取 `AGNES_API_KEY`。仓库不包含密钥、模型权重、生成视频或第三方素材。

## 快速验证

```bash
python3 paper-collage-explainer-video/scripts/init_project.py demo \
  --title "彩虹是怎么形成的" --duration 60 --aspect 16:9

python3 paper-collage-explainer-video/scripts/validate_project.py demo
```

验证技能自身：

```bash
python3 /path/to/skill-creator/scripts/quick_validate.py \
  paper-collage-explainer-video
```

## 目录

```text
paper-collage-explainer-video/
├── SKILL.md
├── agents/openai.yaml
├── references/
│   ├── agnes-ai-video.md
│   ├── art-direction.md
│   ├── high-detail-visual-standard.md
│   ├── schemas.md
│   └── tool-adapters.md
└── scripts/
    ├── agnes_ai_video.py
    ├── edge_xiaoyi_tts.py
    ├── init_project.py
    └── validate_project.py
```

## 许可

代码和文档使用 [MIT License](LICENSE)。第三方服务、模型、字体、音乐、图片和生成内容仍受各自条款约束。
