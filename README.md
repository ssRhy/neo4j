# 化学实验知识图谱

这个项目使用 Python 和 Neo4j 构建一个关于化学实验的知识图谱。知识图谱包含了实验、物质、设备、步骤、安全措施和观察现象等实体及其关系。

## 前提条件

在开始之前，确保您已经：

1. 安装了 Python 3.6+
2. 安装了 Neo4j 数据库（可以是[Neo4j Desktop](https://neo4j.com/download/)或其他部署方式）
3. 创建了一个 Neo4j 数据库实例并已启动

## 安装依赖

```bash
pip install neo4j
```

## 配置

在运行脚本前，请修改`chemistry_kg.py`文件中的以下配置：

```python
# 在main()函数中
uri = "bolt://localhost:7687"  # Neo4j数据库的URI
user = "neo4j"                 # 用户名
password = "password"          # 密码，请替换为您的实际密码
```

## 使用方法

1. 运行脚本以创建化学实验知识图谱：

```bash
python chemistry_kg.py
```

2. 脚本执行后，它将：

   - 连接到您配置的 Neo4j 数据库
   - 创建两个化学实验的示例数据（"加热高锰酸钾制备氧气"和"稀硫酸与铁反应"）
   - 执行一些示例查询并显示结果

3. 打开 Neo4j Browser（通常在`http://localhost:7474`）查看和交互式探索知识图谱

## 知识图谱结构

本知识图谱包含以下节点类型：

- `Experiment`：实验
- `Substance`：物质
- `Equipment`：设备
- `ProcedureStep`：实验步骤
- `SafetyMeasure`：安全措施
- `Hazard`：危险性
- `Observation`：观察现象

以及多种关系类型连接这些节点，形成一个完整的知识网络。

## Cypher 查询示例

在 Neo4j Browser 中，您可以执行以下查询来探索知识图谱：

```cypher
// 显示所有节点和关系
MATCH (n) RETURN n LIMIT 100

// 查询特定实验的完整信息
MATCH (e:Experiment {name: '加热高锰酸钾制备氧气'})
OPTIONAL MATCH (e)-[r1:USES_SUBSTANCE]->(s:Substance)
OPTIONAL MATCH (e)-[r2:USES_EQUIPMENT]->(eq:Equipment)
RETURN e, r1, s, r2, eq

// 查找使用特定物质的所有实验
MATCH (e:Experiment)-[r:USES_SUBSTANCE]->(s:Substance {name: '高锰酸钾'})
RETURN e.name, r.role, s.name, s.formula

// 查找有危险性的物质
MATCH (s:Substance)-[:HAS_HAZARD]->(h:Hazard)
RETURN s.name, collect(h.name) AS hazards
```

## 扩展与定制

您可以通过以下方式扩展和定制此知识图谱：

1. 添加更多实验数据
2. 修改数据模型以适应特定领域需求
3. 添加其他类型的节点和关系
4. 编写更复杂的查询以获取特定的知识洞察

## 故障排除

如果遇到连接问题，请检查：

1. Neo4j 数据库是否正在运行
2. URI、用户名和密码是否正确
3. Neo4j 的网络设置是否允许外部连接
