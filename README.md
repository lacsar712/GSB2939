# LIMS 实验室信息管理系统

一个基于 Vue3 + FastAPI 构建的现代化实验室信息管理系统，支持样品管理、任务分配、数据录入、报告生成等核心功能。

## 🛠 技术栈

- **Frontend**: Vue 3 + Element Plus + Pinia + Vue Router + ECharts
- **Backend**: FastAPI + SQLAlchemy + Pydantic
- **Database**: MySQL 8.0
- **Container**: Docker + Docker Compose

## 🚀 启动指南 (How to Run)

1. 确保 Docker Desktop 已启动
2. 在根目录执行：
```bash
docker compose up --build
```
3. 等待容器启动完成（首次启动约需 3-5 分钟）

## 🔗 服务地址 (Services)

- **Frontend**: http://localhost:3000
- **Backend Swagger**: http://localhost:8000/docs
- **Database**: localhost:3306 (user: lims / pass: lims123)

## 🧪 测试账号

| 用户名 | 密码 | 角色 |
|--------|------|------|
| admin | 123456 | 系统管理员 |
| sample_admin | 123456 | 样品管理员 |
| tester1 | 123456 | 检测人员 |
| tester2 | 123456 | 检测人员 |
| auditor | 123456 | 审核员 |
| issuer | 123456 | 签发人 |
| resource_admin | 123456 | 试剂设备管理员 |

## 📦 功能模块

### 1. 样品管理
- 样品登记（支持手动录入，自动生成编号）
- 样品标识（二维码生成与打印）
- 样品存储（可视化存储看板）
- 流转跟踪（全流程时间轴记录）

### 2. 检验任务管理
- 任务分配（拖拽式分配）
- 标准方法库（国标/行标/企标管理）
- 流程管控（实时进度看板）

### 3. 数据管理
- 检测数据录入（动态表单校验）
- 原始记录管理（在线编辑、审核）
- 数据溯源（树形追溯链）

### 4. 试剂与设备管理
- 试剂台账（库存预警、过期提醒）
- 设备校准（校准计划日历）
- 耗材管理（出入库登记）

### 5. 报告管理
- 报告生成（模板化自动生成）
- 审核签发（多级审核流程）
- 报告模板定制

### 6. 质量合规管理
- 审计追踪（操作日志记录）
- 权限管控（角色权限配置）
- GLP/GMP 规范支持

## 📁 项目结构

```
lims/
├── backend/                 # 后端服务
│   ├── app/
│   │   ├── api/            # API 路由
│   │   ├── models/         # 数据模型
│   │   ├── schemas/        # Pydantic 模型
│   │   ├── core/           # 核心配置
│   │   └── main.py         # 应用入口
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/               # 前端服务
│   ├── src/
│   │   ├── views/          # 页面组件
│   │   ├── components/     # 公共组件
│   │   ├── stores/         # 状态管理
│   │   ├── router/         # 路由配置
│   │   ├── utils/          # 工具函数
│   │   └── assets/         # 静态资源
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml      # 容器编排
└── README.md
```

## 🔧 开发命令

```bash
# 后端开发
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# 前端开发
cd frontend
npm install
npm run dev
```

## 📝 注意事项

- 首次启动会自动初始化数据库并填充演示数据
- 所有密码默认为 `123456`
- 数据库数据存储在 Docker Volume 中，容器删除后数据不会丢失

## 📅 更新日志 (Changelog)

### 2026-02-21
- **核心修复**:
  - 修复样品登记失败问题（优化编号生成逻辑，解决并发写入冲突）。
  - 重构所有业务单据（样品、任务、报告、资源等）的编号生成策略，由 `count()+1` 改为 `max_id+1`，防止删除数据后编号重复。
- **界面优化**:
  - 全局统一表格操作列宽度为 220px，防止按钮换行。
  - 优化样品列表页面的按钮布局与对齐方式。
  - 侧边栏导航菜单增加纵向滚动条，适配小屏幕操作。
  - 任务新建弹窗中的“标准方案”输入框升级为下拉选择组件。
  - 修复列表/看板切换按钮的图标显示问题。
- **Bug Fixes**:
  - 修复试剂、设备新增时因日期格式问题导致的 422 错误。
  - 修复部分页面样式错位问题。

## 📄 License

MIT License
