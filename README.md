# 牛顿环综合实验平台

基于 Python + Tauri 的牛顿环干涉实验教学辅助平台，提供交互式仿真演示、数据处理和 AI 助教功能。

## 功能模块

| 模块 | 状态 |
|------|------|
| 牛顿环干涉仿真演示 | 完整：多种配置（接触/非接触、凹/凸透镜） |
| 实验数据处理 | 完整：线性回归计算曲率半径 |
| PDF 手册集成 | 完整：原理、步骤、分析指南 |
| AI 助教对话 | 完整：基于 DeepSeek-V4 Flash 的流式问答 |


## 技术栈

- **前端**：Vue 3 (Composition API) + Vite + Tailwind CSS v4 + daisyUI v5 + Vue Router + Pinia
- **后端**：Python 3 + FastAPI + Uvicorn + NumPy + Matplotlib
- **AI**：DeepSeek-V4 Flash (via SiliconFlow API)，支持流式 SSE 对话
- **桌面端**：Tauri v2 (Rust) + Nuitka 单文件 Python 侧载
- **目标平台**：Windows (NSIS 安装包)

## 项目结构

```
.
├── server.py              # FastAPI 入口
├── lib/                   # 后端核心
│   ├── api/               # FastAPI 路由 (demo, data, ai)
│   ├── services/          # 业务逻辑层
│   ├── physics.py         # 物理计算引擎
│   ├── plotting.py        # Matplotlib 图像生成
│   ├── ai_module.py       # AI 对话模块
│   └── config.py          # 字体/缓存配置
├── frontend/              # Vue 3 前端
│   ├── src/
│   │   ├── views/         # 页面视图（按实验分目录）
│   │   ├── components/    # 共享组件
│   │   ├── utils/         # 工具类（后端桥接、渲染器、物理计算）
│   │   └── router/        # 路由配置
│   └── public/            # 静态资源（PDF、图片、模板）
├── src-tauri/             # Tauri 桌面应用
│   ├── src/main.rs        # Rust 主进程（管理 Python sidecar）
│   └── tauri.conf.json    # Tauri 配置
├── build.py               # Nuitka 构建 Python sidecar
├── pack.py                # 源码打包工具
├── template.csv           # 实验数据模板
└── qrc/                   # 原始教学资料（PDF、图标）
```

## 开发环境

### 前置依赖

- [Node.js](https://nodejs.org/) (v20+)
- [Python](https://python.org/) (3.11+)
- [Rust](https://rustup.rs/) (Tauri 需要)

### 安装依赖

```bash
# Python 依赖
pip install -r requirements.txt

# Node 依赖（根目录 + 前端）
npm install
cd frontend && npm install
```

## 开发启动

### 方式一：Web 开发模式（推荐前端开发）

终端 1：启动后端
```bash
python server.py
```

终端 2：启动前端
```bash
cd frontend && npm run dev:frontend
```

前端地址：`http://localhost:5173`
后端地址：`http://localhost:8000`

Vite 代理规则自动将 `/api/*`、`/ai_chat`、`/ai_stop`、`/health` 转发到后端。

### 方式二：Tauri 桌面开发模式

```bash
npm run dev
```

启动 Tauri 窗口，同时加载 Vite 开发服务器。

### 方式三：同时启动前后端

```bash
cd frontend && npm run dev
```

## 构建

### 构建 Python Sidecar

```bash
python build.py --force
```

使用 Nuitka 将 `server.py` + `lib/` 编译为单文件可执行程序，输出到 `src-tauri/binaries/backend-x86_64-pc-windows-msvc.exe`。

### 构建完整桌面应用

```bash
npm run build
```

流程：Vite 构建前端 → Tauri 打包 → 生成 NSIS 安装程序（`src-tauri/target/release/bundle/nsis/`）。

### 源码打包

```bash
python pack.py
```

生成不含依赖和构建产物的源码压缩包，用于提交或分发。

## 环境变量

可通过项目根目录 `.env` 文件或系统环境变量配置：

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `AI_API_KEY` | AI 服务 API 密钥 | - |
| `AI_API_BASE_URL` | AI 服务 Base URL | `https://api.siliconflow.cn` |
| `AI_MODEL` | AI 模型名称 | `deepseek-ai/DeepSeek-V4-Flash` |
| `AI_REASONING_EFFORT` | 推理强度 (low/medium/high) | `high` |

示例 `.env`：

```env
AI_API_KEY=your-key
AI_API_BASE_URL=https://api.siliconflow.cn
AI_MODEL=deepseek-ai/DeepSeek-V4-Flash
AI_REASONING_EFFORT=high
```

## 运行模式说明

| 模式 | 前端加载方式 | 后端启动方式 | 适用场景 |
|------|-------------|-------------|---------|
| Web 开发 | Vite dev server (`:5173`) | 手动 `python server.py` | 前端开发调试 |
| Tauri 开发 | Tauri 窗口 → `localhost:5173` | Vite 代理到手动启动的后端 | 桌面端开发调试 |
| 生产桌面 | Tauri 加载 `frontend/dist` 静态文件 | Tauri 自动启动 Python sidecar | 最终用户使用 |

## 核心组件说明

- **`frontend/src/utils/backend-bridge.js`**：前后端通信统一入口，自动识别 Vite 开发环境（走代理）或 Tauri 生产环境（直连 `localhost:8000`）。
- **`lib/physics.py`**：牛顿环空气膜厚度、光强分布、环半径等核心物理计算。
- **`lib/plotting.py`**：干涉环二维彩图、光强曲线、线性回归拟合图生成。
- **`frontend/src/views/newton/components/ExperimentPage.vue`**：牛顿环实验通用页面壳（参数滑块 + Canvas 渲染 + 原理说明）。
- **`frontend/src/views/newton/DataNormal.vue`**：数据录入表格 + 后端线性回归计算曲率半径。

## 许可证

本项目为教学用途开发。
