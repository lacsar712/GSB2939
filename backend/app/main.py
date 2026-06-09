"""
LIMS 系统后端主程序
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import CORS_ORIGINS
from app.core.database import init_db, SessionLocal
from app.api import api_router

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化数据库
    logger.info("Initializing database...")
    init_db()
    
    # 填充初始数据
    logger.info("Seeding initial data...")
    seed_initial_data()
    
    logger.info("Application started successfully")
    yield
    logger.info("Application shutting down...")


def seed_initial_data():
    """填充初始数据"""
    from app.core.security import get_password_hash
    from app.models.user import User, Role, Permission
    from app.models.sample import Sample, SampleStorage
    from app.models.task import Task, StandardMethod
    from app.models.resource import Reagent, Equipment, Consumable
    from app.models.report import ReportTemplate
    from datetime import datetime, timedelta, date
    
    db = SessionLocal()
    try:
        # 创建权限
        permissions = []
        try:
            if not db.query(Permission).first():
                permissions_data = [
                    {"name": "系统管理", "code": "system:manage", "type": "menu", "path": "/system", "icon": "Setting", "sort": 100},
                    {"name": "用户管理", "code": "user:manage", "type": "menu", "path": "/system/users", "icon": "User", "sort": 101},
                    {"name": "角色管理", "code": "role:manage", "type": "menu", "path": "/system/role", "icon": "UserFilled", "sort": 102},
                    {"name": "样品管理", "code": "sample:manage", "type": "menu", "path": "/sample", "icon": "Box", "sort": 200},
                    {"name": "样品登记", "code": "sample:register", "type": "menu", "path": "/sample/register", "icon": "DocumentAdd", "sort": 201},
                    {"name": "样品列表", "code": "sample:list", "type": "menu", "path": "/sample/list", "icon": "List", "sort": 202},
                    {"name": "样品存储", "code": "sample:storage", "type": "menu", "path": "/sample/storage", "icon": "Grid", "sort": 203},
                    {"name": "任务管理", "code": "task:manage", "type": "menu", "path": "/task", "icon": "Tickets", "sort": 300},
                    {"name": "任务列表", "code": "task:list", "type": "menu", "path": "/task/list", "icon": "List", "sort": 301},
                    {"name": "任务分配", "code": "task:assign", "type": "menu", "path": "/task/assign", "icon": "Connection", "sort": 302},
                    {"name": "标准方法", "code": "task:method", "type": "menu", "path": "/task/method", "icon": "Document", "sort": 303},
                    {"name": "数据管理", "code": "data:manage", "type": "menu", "path": "/data", "icon": "DataAnalysis", "sort": 400},
                    {"name": "数据录入", "code": "data:input", "type": "menu", "path": "/data/input", "icon": "Edit", "sort": 401},
                    {"name": "原始记录", "code": "data:record", "type": "menu", "path": "/data/record", "icon": "Tickets", "sort": 402},
                    {"name": "数据溯源", "code": "data:trace", "type": "menu", "path": "/data/trace", "icon": "Share", "sort": 403},
                    {"name": "资源管理", "code": "resource:manage", "type": "menu", "path": "/resource", "icon": "Grid", "sort": 500},
                    {"name": "试剂管理", "code": "resource:reagent", "type": "menu", "path": "/resource/reagent", "icon": "FirstAidKit", "sort": 501},
                    {"name": "设备管理", "code": "resource:equipment", "type": "menu", "path": "/resource/equipment", "icon": "Monitor", "sort": 502},
                    {"name": "耗材管理", "code": "resource:consumable", "type": "menu", "path": "/resource/consumable", "icon": "Box", "sort": 503},
                    {"name": "报告管理", "code": "report:manage", "type": "menu", "path": "/report", "icon": "Document", "sort": 600},
                    {"name": "报告列表", "code": "report:list", "type": "menu", "path": "/report/list", "icon": "List", "sort": 601},
                    {"name": "报告模板", "code": "report:template", "type": "menu", "path": "/report/template", "icon": "Files", "sort": 602},
                    {"name": "质量合规", "code": "quality:manage", "type": "menu", "path": "/quality", "icon": "Medal", "sort": 700},
                    {"name": "审计追踪", "code": "quality:audit", "type": "menu", "path": "/quality/audit", "icon": "View", "sort": 701},
                    {"name": "权限管理", "code": "quality:permission", "type": "menu", "path": "/quality/permission", "icon": "Lock", "sort": 702},
                ]
                
                for perm_data in permissions_data:
                    perm = Permission(**perm_data)
                    db.add(perm)
                db.commit()
                logger.info("Permissions seeded")
            permissions = db.query(Permission).all()
        except Exception as e:
            db.rollback()
            logger.error(f"Error seeding permissions: {e}")
            permissions = db.query(Permission).all()
        
        # 创建角色
        roles = []
        try:
            if not db.query(Role).first():
                roles_data = [
                    {"name": "系统管理员", "code": "admin", "description": "系统管理员，拥有所有权限"},
                    {"name": "样品管理员", "code": "sample_manager", "description": "负责样品管理"},
                    {"name": "检测人员", "code": "tester", "description": "负责检测任务"},
                    {"name": "审核员", "code": "auditor", "description": "负责审核报告"},
                    {"name": "签发人", "code": "issuer", "description": "负责签发报告"},
                    {"name": "试剂设备管理员", "code": "resource_manager", "description": "负责试剂和设备管理"},
                ]
                
                for role_data in roles_data:
                    role = Role(**role_data)
                    db.add(role)
                db.commit()
                
                # 为管理员角色分配所有权限
                admin_role = db.query(Role).filter(Role.code == "admin").first()
                if admin_role:
                    admin_role.permissions = permissions
                    db.commit()
                logger.info("Roles seeded")
            roles = db.query(Role).all()
        except Exception as e:
            db.rollback()
            logger.error(f"Error seeding roles: {e}")
            roles = db.query(Role).all()
        
        # 创建用户
        try:
            if not db.query(User).first():
                # 重新获取角色以确保关联正确
                admin_role = db.query(Role).filter(Role.code == "admin").first()
                sample_role = db.query(Role).filter(Role.code == "sample_manager").first()
                tester_role = db.query(Role).filter(Role.code == "tester").first()
                auditor_role = db.query(Role).filter(Role.code == "auditor").first()
                issuer_role = db.query(Role).filter(Role.code == "issuer").first()
                resource_role = db.query(Role).filter(Role.code == "resource_manager").first()

                users_data = [
                    {"username": "admin", "real_name": "系统管理员", "department": "信息部", "position": "管理员", "role": admin_role},
                    {"username": "sample_admin", "real_name": "张样品", "department": "样品部", "position": "样品管理员", "role": sample_role},
                    {"username": "tester1", "real_name": "李检测", "department": "检测部", "position": "检测员", "role": tester_role},
                    {"username": "tester2", "real_name": "王检测", "department": "检测部", "position": "检测员", "role": tester_role},
                    {"username": "auditor", "real_name": "赵审核", "department": "质量部", "position": "审核员", "role": auditor_role},
                    {"username": "issuer", "real_name": "钱签发", "department": "质量部", "position": "签发人", "role": issuer_role},
                    {"username": "resource_admin", "real_name": "孙资源", "department": "资源部", "position": "资源管理员", "role": resource_role},
                ]
                
                for user_data in users_data:
                    role = user_data.pop("role")
                    if role:
                        user = User(
                            **user_data,
                            password=get_password_hash("123456"),
                            email=f"{user_data['username']}@lims.com"
                        )
                        user.roles = [role]
                        db.add(user)
                db.commit()
                logger.info("Users seeded")
        except Exception as e:
            db.rollback()
            logger.error(f"Error seeding users: {e}")
        
        # 创建存储位置
        try:
            if not db.query(SampleStorage).first():
                storage_data = [
                    {"location_code": "WH-001", "location_name": "主库房", "location_type": "库房", "capacity": 500},
                    {"location_code": "FR-001", "location_name": "1号冰箱", "location_type": "冰箱", "parent_id": 1, "capacity": 100, "temperature": "4℃"},
                    {"location_code": "FR-002", "location_name": "2号冰箱", "location_type": "冰箱", "parent_id": 1, "capacity": 100, "temperature": "-20℃"},
                    {"location_code": "SH-001", "location_name": "A货架", "location_type": "货架", "parent_id": 1, "capacity": 50},
                ]
                
                for storage in storage_data:
                    db.add(SampleStorage(**storage))
                db.commit()
                logger.info("Storage seeded")
        except Exception as e:
            db.rollback()
            logger.error(f"Error seeding storage: {e}")
        
        # 创建标准方法
        try:
            if not db.query(StandardMethod).first():
                methods_data = [
                    {"method_no": "GB-001", "method_name": "食品安全国家标准 食品中铅的测定", "standard_type": "国标", "standard_no": "GB 5009.12-2017"},
                    {"method_no": "GB-002", "method_name": "食品安全国家标准 食品中砷的测定", "standard_type": "国标", "standard_no": "GB 5009.11-2014"},
                    {"method_no": "GB-003", "method_name": "食品安全国家标准 食品中镉的测定", "standard_type": "国标", "standard_no": "GB 5009.15-2014"},
                    {"method_no": "HB-001", "method_name": "化学试剂 水分测定通用方法", "standard_type": "行标", "standard_no": "HG/T 4104-2009"},
                ]
                
                for method in methods_data:
                    db.add(StandardMethod(**method))
                db.commit()
                logger.info("Methods seeded")
        except Exception as e:
            db.rollback()
            logger.error(f"Error seeding methods: {e}")
        
        # 创建样品数据
        try:
            if not db.query(Sample).first():
                samples_data = [
                    {"sample_no": "SP20260101001", "name": "苹果汁样品", "source": "某食品公司", "type": "食品", "customer_name": "某食品公司", "quantity": 500, "unit": "mL", "status": "检测中"},
                    {"sample_no": "SP20260101002", "name": "纯净水样品", "source": "某饮料公司", "type": "饮用水", "customer_name": "某饮料公司", "quantity": 1000, "unit": "mL", "status": "已登记"},
                    {"sample_no": "SP20260101003", "name": "奶粉样品", "source": "某乳业公司", "type": "乳制品", "customer_name": "某乳业公司", "quantity": 200, "unit": "g", "status": "检测中"},
                    {"sample_no": "SP20260101004", "name": "食用油样品", "source": "某粮油公司", "type": "食用油", "customer_name": "某粮油公司", "quantity": 500, "unit": "mL", "status": "检测完成"},
                    {"sample_no": "SP20260101005", "name": "白酒样品", "source": "某酒厂", "type": "酒类", "customer_name": "某酒厂", "quantity": 200, "unit": "mL", "status": "已归档"},
                    {"sample_no": "SP20260101006", "name": "大米样品", "source": "某粮油公司", "type": "粮油", "customer_name": "某粮油公司", "quantity": 1000, "unit": "g", "status": "待检测"},
                    {"sample_no": "SP20260101007", "name": "酱油样品", "source": "某调味品公司", "type": "调味品", "customer_name": "某调味品公司", "quantity": 500, "unit": "mL", "status": "已登记"},
                    {"sample_no": "SP20260101008", "name": "食醋样品", "source": "某调味品公司", "type": "调味品", "customer_name": "某调味品公司", "quantity": 500, "unit": "mL", "status": "待检测"},
                ]
                
                for sample in samples_data:
                    sample["receive_date"] = datetime.now()
                    sample["expected_date"] = datetime.now() + timedelta(days=7)
                    db.add(Sample(**sample))
                db.commit()
                logger.info("Samples seeded")
        except Exception as e:
            db.rollback()
            logger.error(f"Error seeding samples: {e}")
        
        # 创建任务数据
        try:
            if not db.query(Task).first():
                # 获取样品ID
                samples = db.query(Sample).all()
                # Get users for assignment
                tester1 = db.query(User).filter(User.username == "tester1").first()
                tester2 = db.query(User).filter(User.username == "tester2").first()
                admin = db.query(User).filter(User.username == "admin").first()
                
                if samples:
                    tasks_data = [
                        {"task_no": "TK20260101001", "sample_id": samples[0].id, "sample_no": samples[0].sample_no, "sample_name": samples[0].name, "test_items": "铅、砷、镉", "status": "进行中", "priority": "紧急", "department": "检测一部", "assignee_name": "tester1", "assignee_id": tester1.id if tester1 else None, "progress": 60},
                        {"task_no": "TK20260101002", "sample_id": samples[1].id, "sample_no": samples[1].sample_no, "sample_name": samples[1].name, "test_items": "微生物指标", "status": "待分配", "priority": "普通", "department": "检测二部"},
                        {"task_no": "TK20260101003", "sample_id": samples[2].id, "sample_no": samples[2].sample_no, "sample_name": samples[2].name, "test_items": "蛋白质、脂肪", "status": "待接收", "priority": "普通", "department": "检测一部", "assignee_name": "tester2", "assignee_id": tester2.id if tester2 else None},
                        {"task_no": "TK20260101004", "sample_id": samples[3].id, "sample_no": samples[3].sample_no, "sample_name": samples[3].name, "test_items": "酸价、过氧化值", "status": "已完成", "priority": "普通", "department": "检测二部", "assignee_name": "tester1", "assignee_id": tester1.id if tester1 else None, "progress": 100},
                        {"task_no": "TK20260101005", "sample_id": samples[5].id, "sample_no": samples[5].sample_no, "sample_name": samples[5].name, "test_items": "黄曲霉毒素", "status": "待分配", "priority": "紧急", "department": "检测一部"},
                        {"task_no": "TK20260101006", "sample_id": samples[7].id, "sample_no": samples[7].sample_no, "sample_name": samples[7].name, "test_items": "总酸", "status": "进行中", "priority": "普通", "department": "检测二部", "assignee_name": "tester2", "assignee_id": tester2.id if tester2 else None, "progress": 30},
                    ]
                    
                    for task in tasks_data:
                        task["deadline"] = datetime.now() + timedelta(days=5)
                        if admin:
                            task["created_by"] = admin.id
                        db.add(Task(**task))
                    db.commit()
                    logger.info("Tasks seeded")
        except Exception as e:
            db.rollback()
            logger.error(f"Error seeding tasks: {e}")
        
        # 创建试剂数据
        try:
            if not db.query(Reagent).first():
                reagents_data = [
                    {"reagent_no": "RG20260101001", "name": "硝酸", "specification": "优级纯", "manufacturer": "某化工厂", "category": "酸类", "quantity": 500, "unit": "mL", "warning_quantity": 100, "expiry_date": date(2027, 1, 1)},
                    {"reagent_no": "RG20260101002", "name": "盐酸", "specification": "优级纯", "manufacturer": "某化工厂", "category": "酸类", "quantity": 800, "unit": "mL", "warning_quantity": 100, "expiry_date": date(2027, 6, 1)},
                    {"reagent_no": "RG20260101003", "name": "硫酸", "specification": "优级纯", "manufacturer": "某化工厂", "category": "酸类", "quantity": 50, "unit": "mL", "warning_quantity": 100, "expiry_date": date(2026, 6, 1)},
                    {"reagent_no": "RG20260101004", "name": "乙醇", "specification": "分析纯", "manufacturer": "某试剂厂", "category": "有机溶剂", "quantity": 1000, "unit": "mL", "warning_quantity": 200, "expiry_date": date(2028, 1, 1)},
                    {"reagent_no": "RG20260101005", "name": "甲醇", "specification": "色谱纯", "manufacturer": "某试剂厂", "category": "有机溶剂", "quantity": 4000, "unit": "mL", "warning_quantity": 500, "expiry_date": date(2026, 12, 1)},
                ]
                
                for reagent in reagents_data:
                    db.add(Reagent(**reagent))
                db.commit()
                logger.info("Reagents seeded")
        except Exception as e:
            db.rollback()
            logger.error(f"Error seeding reagents: {e}")
        
        # 创建设备数据
        try:
            if not db.query(Equipment).first():
                equipments_data = [
                    {"equipment_no": "EQ20260101001", "name": "原子吸收光谱仪", "model": "AA-7000", "manufacturer": "某仪器公司", "category": "分析仪器", "status": "正常", "responsible_person": "李检测", "next_calibration_date": date(2026, 6, 1)},
                    {"equipment_no": "EQ20260101002", "name": "气相色谱仪", "model": "GC-2010", "manufacturer": "某仪器公司", "category": "分析仪器", "status": "正常", "responsible_person": "王检测", "next_calibration_date": date(2026, 7, 1)},
                    {"equipment_no": "EQ20260101003", "name": "电子天平", "model": "ME204", "manufacturer": "某仪器公司", "category": "称量设备", "status": "正常", "responsible_person": "张样品", "next_calibration_date": date(2026, 4, 1)},
                    {"equipment_no": "EQ20260101004", "name": "pH计", "model": "PHS-3C", "manufacturer": "某仪器公司", "category": "分析仪器", "status": "维修中", "responsible_person": "王检测"},
                    {"equipment_no": "EQ20260101005", "name": "液相色谱仪", "model": "LC-20A", "manufacturer": "某仪器公司", "category": "分析仪器", "status": "正常", "responsible_person": "李检测", "next_calibration_date": date(2026, 8, 1)},
                ]
                
                for equipment in equipments_data:
                    db.add(Equipment(**equipment))
                db.commit()
                logger.info("Equipments seeded")
        except Exception as e:
            db.rollback()
            logger.error(f"Error seeding equipments: {e}")
        
        # 创建耗材数据
        try:
            if not db.query(Consumable).first():
                consumables_data = [
                    {"consumable_no": "CS20260101001", "name": "移液管", "specification": "10mL", "category": "玻璃器皿", "quantity": 50, "unit": "支", "warning_quantity": 10},
                    {"consumable_no": "CS20260101002", "name": "容量瓶", "specification": "100mL", "category": "玻璃器皿", "quantity": 30, "unit": "个", "warning_quantity": 5},
                    {"consumable_no": "CS20260101003", "name": "滤纸", "specification": "定性", "category": "过滤耗材", "quantity": 500, "unit": "张", "warning_quantity": 50},
                    {"consumable_no": "CS20260101004", "name": "一次性手套", "specification": "L号", "category": "防护用品", "quantity": 100, "unit": "双", "warning_quantity": 20},
                    {"consumable_no": "CS20260101005", "name": "针头过滤器", "specification": "0.45um", "category": "过滤耗材", "quantity": 200, "unit": "个", "warning_quantity": 20},
                ]
                
                for consumable in consumables_data:
                    db.add(Consumable(**consumable))
                db.commit()
                logger.info("Consumables seeded")
        except Exception as e:
            db.rollback()
            logger.error(f"Error seeding consumables: {e}")
        
        # 创建报告模板
        templates_data = [
            {"template_no": "TPL-001", "template_name": "食品检测报告模板", "template_type": "食品类", "is_default": True},
            {"template_no": "TPL-002", "template_name": "水质检测报告模板", "template_type": "水质类", "is_default": False},
        ]
        
        for template in templates_data:
            db.add(ReportTemplate(**template))
        db.commit()
        
        logger.info("Initial data seeded successfully")
        
    except Exception as e:
        logger.error(f"Error seeding data: {e}")
        db.rollback()
    finally:
        db.close()


# 创建应用
app = FastAPI(
    title="LIMS 实验室信息管理系统",
    description="实验室信息管理系统后端API",
    version="1.0.0",
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(api_router, prefix="/api")


@app.get("/")
def root():
    """根路径"""
    return {"message": "LIMS API", "version": "1.0.0", "docs": "/docs"}


@app.get("/health")
def health_check():
    """健康检查"""
    return {"status": "healthy"}
