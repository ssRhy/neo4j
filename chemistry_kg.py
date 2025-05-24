#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
化学实验知识图谱构建脚本
此脚本用于构建一个关于化学实验的Neo4j知识图谱
"""

from neo4j import GraphDatabase
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ChemistryKnowledgeGraph:
    """用于创建和管理化学实验知识图谱的类"""

    def __init__(self, uri, user, password):
        """
        初始化Neo4j数据库连接
        
        :param uri: bolt://localhost:7687
        :param user: neo4j
        :param password: 123456
        """
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        logger.info("已连接到Neo4j数据库")

    def close(self):
        """关闭数据库连接"""
        if self.driver:
            self.driver.close()
            logger.info("已关闭Neo4j连接")

    def _execute_query(self, query, parameters=None):
        """
        执行Cypher查询
        
        :param query: Cypher查询语句
        :param parameters: 查询参数
        :return: 查询结果
        """
        with self.driver.session() as session:
            result = session.run(query, parameters or {})
            return [record for record in result]

    def clear_database(self):
        """清空数据库"""
        logger.warning("清空数据库中的所有数据")
        query = "MATCH (n) DETACH DELETE n"
        self._execute_query(query)
        logger.info("数据库已清空")

    # 节点创建方法
    def add_experiment(self, name, objective=None, date=None, description=None):
        """
        添加实验节点
        
        :param name: 实验名称
        :param objective: 实验目的
        :param date: 实验日期
        :param description: 实验描述
        :return: 创建的节点信息
        """
        query = """
        MERGE (e:Experiment {name: $name})
        ON CREATE SET e.created_at = datetime()
        """
        
        # 动态添加可选参数
        set_clauses = []
        params = {"name": name}
        
        if objective:
            set_clauses.append("e.objective = $objective")
            params["objective"] = objective
        
        if date:
            set_clauses.append("e.date = $date")
            params["date"] = date
            
        if description:
            set_clauses.append("e.description = $description")
            params["description"] = description
        
        if set_clauses:
            query += f" SET {', '.join(set_clauses)}"
            
        query += " RETURN e.name AS name"
        
        result = self._execute_query(query, params)
        logger.info(f"已添加实验: {name}")
        return result

    def add_substance(self, name, formula=None, state=None, cas_number=None, molecular_weight=None):
        """
        添加物质节点
        
        :param name: 物质名称
        :param formula: 化学式
        :param state: 状态(固体/液体/气体)
        :param cas_number: CAS号
        :param molecular_weight: 分子量
        :return: 创建的节点信息
        """
        query = """
        MERGE (s:Substance {name: $name})
        ON CREATE SET s.created_at = datetime()
        """
        
        # 动态添加可选参数
        set_clauses = []
        params = {"name": name}
        
        if formula:
            set_clauses.append("s.formula = $formula")
            params["formula"] = formula
        
        if state:
            set_clauses.append("s.state = $state")
            params["state"] = state
            
        if cas_number:
            set_clauses.append("s.cas_number = $cas_number")
            params["cas_number"] = cas_number
            
        if molecular_weight:
            set_clauses.append("s.molecular_weight = $molecular_weight")
            params["molecular_weight"] = molecular_weight
        
        if set_clauses:
            query += f" SET {', '.join(set_clauses)}"
            
        query += " RETURN s.name AS name, s.formula AS formula"
        
        result = self._execute_query(query, params)
        logger.info(f"已添加物质: {name}")
        return result

    def add_equipment(self, name, type=None, description=None):
        """
        添加设备节点
        
        :param name: 设备名称
        :param type: 设备类型
        :param description: 设备描述
        :return: 创建的节点信息
        """
        query = """
        MERGE (e:Equipment {name: $name})
        ON CREATE SET e.created_at = datetime()
        """
        
        # 动态添加可选参数
        set_clauses = []
        params = {"name": name}
        
        if type:
            set_clauses.append("e.type = $type")
            params["type"] = type
        
        if description:
            set_clauses.append("e.description = $description")
            params["description"] = description
        
        if set_clauses:
            query += f" SET {', '.join(set_clauses)}"
            
        query += " RETURN e.name AS name, e.type AS type"
        
        result = self._execute_query(query, params)
        logger.info(f"已添加设备: {name}")
        return result

    def add_procedure_step(self, description, order=None):
        """
        添加实验步骤节点
        
        :param description: 步骤描述
        :param order: 步骤顺序
        :return: 创建的节点信息
        """
        query = """
        CREATE (p:ProcedureStep {description: $description})
        """
        
        params = {"description": description}
        
        if order is not None:
            query += " SET p.order = $order"
            params["order"] = order
            
        query += " RETURN p.description AS description, p.order AS order"
        
        result = self._execute_query(query, params)
        logger.info(f"已添加实验步骤: {description[:20]}...")
        return result

    def add_safety_measure(self, description, type=None):
        """
        添加安全措施节点
        
        :param description: 安全措施描述
        :param type: 安全措施类型
        :return: 创建的节点信息
        """
        query = """
        CREATE (s:SafetyMeasure {description: $description})
        """
        
        params = {"description": description}
        
        if type:
            query += " SET s.type = $type"
            params["type"] = type
            
        query += " RETURN s.description AS description"
        
        result = self._execute_query(query, params)
        logger.info(f"已添加安全措施: {description[:20]}...")
        return result

    def add_hazard(self, name, description=None, level=None):
        """
        添加危险性节点
        
        :param name: 危险性名称
        :param description: 描述
        :param level: 危险等级
        :return: 创建的节点信息
        """
        query = """
        MERGE (h:Hazard {name: $name})
        """
        
        params = {"name": name}
        set_clauses = []
        
        if description:
            set_clauses.append("h.description = $description")
            params["description"] = description
        
        if level:
            set_clauses.append("h.level = $level")
            params["level"] = level
            
        if set_clauses:
            query += f" SET {', '.join(set_clauses)}"
            
        query += " RETURN h.name AS name"
        
        result = self._execute_query(query, params)
        logger.info(f"已添加危险性: {name}")
        return result

    def add_observation(self, description, experiment_name=None):
        """
        添加观察现象节点
        
        :param description: 现象描述
        :param experiment_name: 关联的实验名称
        :return: 创建的节点信息
        """
        query = """
        CREATE (o:Observation {description: $description})
        """
        
        params = {"description": description}
        
        result = self._execute_query(query, params)
        
        # 如果提供了实验名称，则创建关系
        if experiment_name:
            self.link_experiment_observation(experiment_name, description)
            
        logger.info(f"已添加观察现象: {description[:20]}...")
        return result

    # 关系创建方法
    def link_experiment_substance(self, experiment_name, substance_name, role, quantity=None):
        """
        连接实验和物质
        
        :param experiment_name: 实验名称
        :param substance_name: 物质名称
        :param role: 角色 (如"反应物"、"产物"、"催化剂"等)
        :param quantity: 用量
        :return: 创建的关系信息
        """
        query = """
        MATCH (e:Experiment {name: $experiment_name})
        MATCH (s:Substance {name: $substance_name})
        MERGE (e)-[r:USES_SUBSTANCE {role: $role}]->(s)
        """
        
        params = {
            "experiment_name": experiment_name,
            "substance_name": substance_name,
            "role": role
        }
        
        if quantity:
            query += " SET r.quantity = $quantity"
            params["quantity"] = quantity
            
        query += " RETURN type(r) AS relationship_type"
        
        result = self._execute_query(query, params)
        logger.info(f"已连接实验 '{experiment_name}' 与物质 '{substance_name}' (角色: {role})")
        return result

    def link_experiment_equipment(self, experiment_name, equipment_name, purpose=None):
        """
        连接实验和设备
        
        :param experiment_name: 实验名称
        :param equipment_name: 设备名称
        :param purpose: 用途
        :return: 创建的关系信息
        """
        query = """
        MATCH (e:Experiment {name: $experiment_name})
        MATCH (eq:Equipment {name: $equipment_name})
        MERGE (e)-[r:USES_EQUIPMENT]->(eq)
        """
        
        params = {
            "experiment_name": experiment_name,
            "equipment_name": equipment_name
        }
        
        if purpose:
            query += " SET r.purpose = $purpose"
            params["purpose"] = purpose
            
        query += " RETURN type(r) AS relationship_type"
        
        result = self._execute_query(query, params)
        logger.info(f"已连接实验 '{experiment_name}' 与设备 '{equipment_name}'")
        return result

    def link_experiment_step(self, experiment_name, step_description):
        """
        连接实验和步骤
        
        :param experiment_name: 实验名称
        :param step_description: 步骤描述
        :return: 创建的关系信息
        """
        query = """
        MATCH (e:Experiment {name: $experiment_name})
        MATCH (p:ProcedureStep {description: $step_description})
        MERGE (e)-[r:HAS_STEP]->(p)
        RETURN type(r) AS relationship_type
        """
        
        params = {
            "experiment_name": experiment_name,
            "step_description": step_description
        }
        
        result = self._execute_query(query, params)
        logger.info(f"已连接实验 '{experiment_name}' 与步骤")
        return result

    def link_steps_sequence(self, previous_step_desc, next_step_desc):
        """
        连接两个步骤，表示顺序
        
        :param previous_step_desc: 前一个步骤描述
        :param next_step_desc: 后一个步骤描述
        :return: 创建的关系信息
        """
        query = """
        MATCH (p1:ProcedureStep {description: $previous_step_desc})
        MATCH (p2:ProcedureStep {description: $next_step_desc})
        MERGE (p1)-[r:NEXT_STEP]->(p2)
        RETURN type(r) AS relationship_type
        """
        
        params = {
            "previous_step_desc": previous_step_desc,
            "next_step_desc": next_step_desc
        }
        
        result = self._execute_query(query, params)
        logger.info(f"已连接步骤顺序")
        return result

    def link_substance_hazard(self, substance_name, hazard_name):
        """
        连接物质和危险性
        
        :param substance_name: 物质名称
        :param hazard_name: 危险性名称
        :return: 创建的关系信息
        """
        query = """
        MATCH (s:Substance {name: $substance_name})
        MATCH (h:Hazard {name: $hazard_name})
        MERGE (s)-[r:HAS_HAZARD]->(h)
        RETURN type(r) AS relationship_type
        """
        
        params = {
            "substance_name": substance_name,
            "hazard_name": hazard_name
        }
        
        result = self._execute_query(query, params)
        logger.info(f"已连接物质 '{substance_name}' 与危险性 '{hazard_name}'")
        return result

    def link_experiment_safety(self, experiment_name, safety_description):
        """
        连接实验和安全措施
        
        :param experiment_name: 实验名称
        :param safety_description: 安全措施描述
        :return: 创建的关系信息
        """
        query = """
        MATCH (e:Experiment {name: $experiment_name})
        MATCH (s:SafetyMeasure {description: $safety_description})
        MERGE (e)-[r:REQUIRES_SAFETY_MEASURE]->(s)
        RETURN type(r) AS relationship_type
        """
        
        params = {
            "experiment_name": experiment_name,
            "safety_description": safety_description
        }
        
        result = self._execute_query(query, params)
        logger.info(f"已连接实验 '{experiment_name}' 与安全措施")
        return result

    def link_substances_reaction(self, reactant_name, product_name, reaction_type=None, conditions=None):
        """
        连接反应物和产物
        
        :param reactant_name: 反应物名称
        :param product_name: 产物名称
        :param reaction_type: 反应类型
        :param conditions: 反应条件
        :return: 创建的关系信息
        """
        query = """
        MATCH (r:Substance {name: $reactant_name})
        MATCH (p:Substance {name: $product_name})
        MERGE (r)-[rel:REACTS_TO]->(p)
        """
        
        params = {
            "reactant_name": reactant_name,
            "product_name": product_name
        }
        
        set_clauses = []
        
        if reaction_type:
            set_clauses.append("rel.reaction_type = $reaction_type")
            params["reaction_type"] = reaction_type
            
        if conditions:
            set_clauses.append("rel.conditions = $conditions")
            params["conditions"] = conditions
            
        if set_clauses:
            query += f" SET {', '.join(set_clauses)}"
            
        query += " RETURN type(rel) AS relationship_type"
        
        result = self._execute_query(query, params)
        logger.info(f"已连接物质 '{reactant_name}' 与产物 '{product_name}'")
        return result
        
    def link_experiment_observation(self, experiment_name, observation_description):
        """
        连接实验和观察现象
        
        :param experiment_name: 实验名称
        :param observation_description: 现象描述
        :return: 创建的关系信息
        """
        query = """
        MATCH (e:Experiment {name: $experiment_name})
        MATCH (o:Observation {description: $observation_description})
        MERGE (e)-[r:HAS_OBSERVATION]->(o)
        RETURN type(r) AS relationship_type
        """
        
        params = {
            "experiment_name": experiment_name,
            "observation_description": observation_description
        }
        
        result = self._execute_query(query, params)
        logger.info(f"已连接实验 '{experiment_name}' 与观察现象")
        return result
        
    # 查询方法
    def find_experiments_using_substance(self, substance_name):
        """
        查找使用指定物质的实验
        
        :param substance_name: 物质名称
        :return: 查询结果
        """
        query = """
        MATCH (e:Experiment)-[:USES_SUBSTANCE]->(s:Substance {name: $substance_name})
        RETURN e.name AS experiment_name, e.objective AS experiment_objective
        """
        
        result = self._execute_query(query, {"substance_name": substance_name})
        
        if not result:
            logger.info(f"没有找到使用 '{substance_name}' 的实验")
        else:
            logger.info(f"找到 {len(result)} 个使用 '{substance_name}' 的实验")
            
        return result
        
    def find_substances_by_state(self, state):
        """
        根据状态查找物质
        
        :param state: 物质状态 (固体/液体/气体)
        :return: 查询结果
        """
        query = """
        MATCH (s:Substance)
        WHERE s.state = $state
        RETURN s.name AS name, s.formula AS formula
        """
        
        result = self._execute_query(query, {"state": state})
        
        if not result:
            logger.info(f"没有找到状态为 '{state}' 的物质")
        else:
            logger.info(f"找到 {len(result)} 个状态为 '{state}' 的物质")
            
        return result
        
    def find_experiment_steps(self, experiment_name):
        """
        查找实验的所有步骤
        
        :param experiment_name: 实验名称
        :return: 查询结果
        """
        query = """
        MATCH (e:Experiment {name: $experiment_name})-[:HAS_STEP]->(p:ProcedureStep)
        RETURN p.description AS description, p.order AS order
        ORDER BY p.order
        """
        
        result = self._execute_query(query, {"experiment_name": experiment_name})
        
        if not result:
            logger.info(f"没有找到实验 '{experiment_name}' 的步骤")
        else:
            logger.info(f"找到实验 '{experiment_name}' 的 {len(result)} 个步骤")
            
        return result
        
    def find_hazardous_substances(self):
        """
        查找有危险性的物质
        
        :return: 查询结果
        """
        query = """
        MATCH (s:Substance)-[:HAS_HAZARD]->(h:Hazard)
        RETURN s.name AS substance_name, collect(h.name) AS hazards
        """
        
        result = self._execute_query(query)
        
        if not result:
            logger.info("没有找到有危险性的物质")
        else:
            logger.info(f"找到 {len(result)} 个有危险性的物质")
            
        return result
        
    def get_experiment_complete_info(self, experiment_name):
        """
        获取实验的完整信息
        
        :param experiment_name: 实验名称
        :return: 查询结果
        """
        query = """
        MATCH (e:Experiment {name: $experiment_name})
        OPTIONAL MATCH (e)-[:USES_SUBSTANCE]->(s:Substance)
        OPTIONAL MATCH (e)-[:USES_EQUIPMENT]->(eq:Equipment)
        OPTIONAL MATCH (e)-[:HAS_STEP]->(p:ProcedureStep)
        OPTIONAL MATCH (e)-[:REQUIRES_SAFETY_MEASURE]->(sm:SafetyMeasure)
        RETURN 
            e.name AS name, 
            e.objective AS objective,
            collect(DISTINCT {name: s.name, formula: s.formula, role: null}) AS substances,
            collect(DISTINCT {name: eq.name, type: eq.type}) AS equipment,
            collect(DISTINCT {description: p.description, order: p.order}) AS steps,
            collect(DISTINCT sm.description) AS safety_measures
        """
        
        result = self._execute_query(query, {"experiment_name": experiment_name})
        
        if not result:
            logger.info(f"没有找到实验 '{experiment_name}' 的信息")
        else:
            logger.info(f"已获取实验 '{experiment_name}' 的完整信息")
            
        return result

# 创建示例数据
def create_example_data(kg):
    """创建示例数据"""
    
    # 1. 加热高锰酸钾制备氧气
    exp1 = "加热高锰酸钾制备氧气"
    kg.add_experiment(exp1, "学习氧气的制备方法和性质", "2023-01-15", "通过加热高锰酸钾制备氧气，并研究其性质")
    
    # 添加物质
    kg.add_substance("高锰酸钾", "KMnO₄", "固体", "7722-64-7", 158.034)
    kg.add_substance("二氧化锰", "MnO₂", "固体", "1313-13-9", 86.9368)
    kg.add_substance("氧气", "O₂", "气体", "7782-44-7", 31.9988)
    
    # 添加设备
    kg.add_equipment("试管", "玻璃仪器", "用于容纳和加热反应物")
    kg.add_equipment("酒精灯", "加热设备", "提供加热源")
    kg.add_equipment("导管", "连接装置", "引导气体")
    kg.add_equipment("集气瓶", "收集装置", "收集气体")
    kg.add_equipment("木条", "测试工具", "测试氧气性质")
    
    # 添加步骤
    step1 = "将少量高锰酸钾放入试管中"
    step2 = "用酒精灯加热试管底部"
    step3 = "观察反应现象"
    step4 = "用导管将产生的气体导入集气瓶中"
    step5 = "取一根带火星的木条伸入集气瓶，观察现象"
    
    kg.add_procedure_step(step1, 1)
    kg.add_procedure_step(step2, 2)
    kg.add_procedure_step(step3, 3)
    kg.add_procedure_step(step4, 4)
    kg.add_procedure_step(step5, 5)
    
    # 添加安全措施
    safety1 = "佩戴防护眼镜"
    safety2 = "试管口不要对着人"
    safety3 = "试管底部要均匀受热"
    
    kg.add_safety_measure(safety1, "个人防护")
    kg.add_safety_measure(safety2, "操作安全")
    kg.add_safety_measure(safety3, "设备安全")
    
    # 添加危险性
    kg.add_hazard("氧化性", "可引起其他物质燃烧", "高")
    kg.add_hazard("刺激性", "对粘膜有刺激性", "中")
    
    # 添加观察现象
    obs1 = "高锰酸钾受热后熔化并放出气泡"
    obs2 = "带火星的木条在气体中复燃并剧烈燃烧"
    
    kg.add_observation(obs1)
    kg.add_observation(obs2)
    
    # 建立关系
    kg.link_experiment_substance(exp1, "高锰酸钾", "反应物", "少量")
    kg.link_experiment_substance(exp1, "二氧化锰", "产物")
    kg.link_experiment_substance(exp1, "氧气", "产物")
    
    kg.link_experiment_equipment(exp1, "试管", "容纳反应物")
    kg.link_experiment_equipment(exp1, "酒精灯", "加热反应物")
    kg.link_experiment_equipment(exp1, "导管", "导出气体")
    kg.link_experiment_equipment(exp1, "集气瓶", "收集气体")
    kg.link_experiment_equipment(exp1, "木条", "测试气体性质")
    
    kg.link_experiment_step(exp1, step1)
    kg.link_experiment_step(exp1, step2)
    kg.link_experiment_step(exp1, step3)
    kg.link_experiment_step(exp1, step4)
    kg.link_experiment_step(exp1, step5)
    
    kg.link_steps_sequence(step1, step2)
    kg.link_steps_sequence(step2, step3)
    kg.link_steps_sequence(step3, step4)
    kg.link_steps_sequence(step4, step5)
    
    kg.link_substance_hazard("高锰酸钾", "氧化性")
    kg.link_substance_hazard("高锰酸钾", "刺激性")
    
    kg.link_experiment_safety(exp1, safety1)
    kg.link_experiment_safety(exp1, safety2)
    kg.link_experiment_safety(exp1, safety3)
    
    kg.link_substances_reaction("高锰酸钾", "二氧化锰", "分解反应", "加热")
    kg.link_substances_reaction("高锰酸钾", "氧气", "分解反应", "加热")
    
    kg.link_experiment_observation(exp1, obs1)
    kg.link_experiment_observation(exp1, obs2)
    
    # 2. 稀硫酸与铁反应
    exp2 = "稀硫酸与铁反应"
    kg.add_experiment(exp2, "观察金属与酸的反应", "2023-01-20", "研究稀硫酸与铁反应生成硫酸亚铁和氢气")
    
    # 添加物质
    kg.add_substance("铁", "Fe", "固体", "7439-89-6", 55.845)
    kg.add_substance("稀硫酸", "H₂SO₄(aq)", "液体", "7664-93-9", 98.079)
    kg.add_substance("硫酸亚铁", "FeSO₄", "固体", "7720-78-7", 151.908)
    kg.add_substance("氢气", "H₂", "气体", "1333-74-0", 2.016)
    
    # 添加步骤
    step1_2 = "将铁屑放入试管中"
    step2_2 = "加入稀硫酸"
    step3_2 = "观察反应现象"
    step4_2 = "用导管收集气体"
    step5_2 = "用点燃的火柴靠近气体，观察现象"
    
    kg.add_procedure_step(step1_2, 1)
    kg.add_procedure_step(step2_2, 2)
    kg.add_procedure_step(step3_2, 3)
    kg.add_procedure_step(step4_2, 4)
    kg.add_procedure_step(step5_2, 5)
    
    # 添加观察现象
    obs1_2 = "铁与稀硫酸接触后产生气泡"
    obs2_2 = "溶液逐渐变为浅绿色"
    obs3_2 = "收集的气体遇火发出轻微的爆鸣声"
    
    kg.add_observation(obs1_2)
    kg.add_observation(obs2_2)
    kg.add_observation(obs3_2)
    
    # 添加危险性
    kg.add_hazard("腐蚀性", "对皮肤和眼睛有腐蚀性", "高")
    kg.add_hazard("易燃性", "在空气中易燃易爆", "高")
    
    # 建立关系
    kg.link_experiment_substance(exp2, "铁", "反应物", "少量")
    kg.link_experiment_substance(exp2, "稀硫酸", "反应物", "适量")
    kg.link_experiment_substance(exp2, "硫酸亚铁", "产物")
    kg.link_experiment_substance(exp2, "氢气", "产物")
    
    kg.link_experiment_equipment(exp2, "试管", "容纳反应物")
    kg.link_experiment_equipment(exp2, "导管", "导出气体")
    
    kg.link_experiment_step(exp2, step1_2)
    kg.link_experiment_step(exp2, step2_2)
    kg.link_experiment_step(exp2, step3_2)
    kg.link_experiment_step(exp2, step4_2)
    kg.link_experiment_step(exp2, step5_2)
    
    kg.link_steps_sequence(step1_2, step2_2)
    kg.link_steps_sequence(step2_2, step3_2)
    kg.link_steps_sequence(step3_2, step4_2)
    kg.link_steps_sequence(step4_2, step5_2)
    
    kg.link_substance_hazard("稀硫酸", "腐蚀性")
    kg.link_substance_hazard("氢气", "易燃性")
    
    kg.link_experiment_safety(exp2, safety1)
    kg.link_experiment_safety(exp2, "操作时避免酸溶液溅到皮肤上")
    
    kg.link_substances_reaction("铁", "硫酸亚铁", "置换反应", "常温")
    kg.link_substances_reaction("铁", "氢气", "置换反应", "常温")
    
    kg.link_experiment_observation(exp2, obs1_2)
    kg.link_experiment_observation(exp2, obs2_2)
    kg.link_experiment_observation(exp2, obs3_2)
    
    logger.info("已成功创建示例数据")

def main():
    """主函数"""
    # 这里需要替换为你的Neo4j连接信息
    uri = "neo4j://localhost:7687"
    user = "neo4j"
    password = "han3241936357"  # 请替换为你的密码
    
    try:
        # 连接到Neo4j数据库
        kg = ChemistryKnowledgeGraph(uri, user, password)
        
        # 清空数据库（可选，取消注释以清空数据库）
        # kg.clear_database()
        
        # 创建示例数据
        create_example_data(kg)
        
        # 执行一些查询示例
        print("\n使用高锰酸钾的实验:")
        results = kg.find_experiments_using_substance("高锰酸钾")
        for result in results:
            print(f"- {result['experiment_name']}: {result['experiment_objective']}")
        
        print("\n气体状态的物质:")
        results = kg.find_substances_by_state("气体")
        for result in results:
            print(f"- {result['name']} ({result['formula'] if result['formula'] else 'N/A'})")
        
        print("\n加热高锰酸钾制备氧气实验的步骤:")
        results = kg.find_experiment_steps("加热高锰酸钾制备氧气")
        for result in results:
            print(f"{result['order']}. {result['description']}")
        
        print("\n具有危险性的物质:")
        results = kg.find_hazardous_substances()
        for result in results:
            print(f"- {result['substance_name']}: {', '.join(result['hazards'])}")
        
    except Exception as e:
        logger.error(f"发生错误: {e}")
    finally:
        # 关闭数据库连接
        if 'kg' in locals():
            kg.close()

if __name__ == "__main__":
    main() 