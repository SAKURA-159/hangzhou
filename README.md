# 杭州房价分析仪表盘（Streamlit）

一个基于 Streamlit 的交互式房价分析看板，支持区域/价格/类型筛选、区域与价格可视化分析，并在「价值发现」模块基于区域基准价（均值/中位数）计算折扣比例筛选潜在性价比楼盘。

仓库中还包含 **FastAPI 后端 + Streamlit 前端**（`backend/`、`frontend/`）、Docker、测试与随机森林预测模块；根目录 **`app.py`** 为可单独运行的单机版仪表盘。

## 项目结构（概要）

- `app.py` — 单机 Streamlit 仪表盘（读取 `data/*.csv`）
- `requirements.txt` — 单机版依赖
- `backend/`、`frontend/` — 前后端分离完整栈
- `data/` — CSV 数据

## Streamlit Cloud 部署（根目录单机版）

你无法只在对话里完成托管：**必须在 [Streamlit Community Cloud](https://share.streamlit.io)** 用 GitHub 登录后创建应用。仓库已包含根目录 `requirements.txt` 与 `.streamlit/config.toml`，按下面选即可。

1. 打开 [share.streamlit.io](https://share.streamlit.io)，用 GitHub 登录。
2. **New app** → 选择仓库 **`SAKURA-159/hangzhou`**，分支 **`master`**。
3. **Main file path** 填：**`app.py`**（不要用 `frontend/app.py`，除非你已单独部署后端并配置密钥）。
4. **App URL** 可用默认，点击 **Deploy**。
5. 首次构建约 1～3 分钟；成功后浏览器会得到 `https://xxx.streamlit.app` 链接。

**说明：** 单机版不依赖数据库与 JWT，无需在 Cloud 里配置 Secrets。若将来要部署 **`frontend/app.py`**，需先将 API 部署到公网，并在 Streamlit Cloud **Secrets** 中设置 `API_BASE_URL`。

## 本地运行（单机版）

```bash
pip install -r requirements.txt
streamlit run app.py
```

## 本地运行（前后端）

参见仓库内 `docker-compose.yml`、`start.bat` 或 `backend` / `frontend` 目录说明。
