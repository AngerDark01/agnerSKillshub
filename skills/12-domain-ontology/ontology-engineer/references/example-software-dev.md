# 示例本体：软件研发领域

## 场景：需求溯源与故障排查

### 能力问题（CQs）

| CQ | 问题 | 驱动的核心概念 |
|----|------|--------------|
| CQ1 | 导致"支付失败（Bug-404）"的这行代码，是谁提交的？ | Commit、Bug、Developer |
| CQ2 | 业务线提的"购物车满减（Req-001）"，有没有对应测试用例覆盖？ | RequirementDoc、TestCase、SourceCode |
| CQ3 | 如果"用户服务（User Service）"宕机，会级联影响哪些微服务？ | Microservice、dependsOn（传递性） |

---

## 类树（T-Box / Classes）

```
Person
  ├── Developer
  ├── Tester
  └── ProductManager

Artifact
  ├── RequirementDoc
  ├── SourceCode
  │     └── Commit
  └── TestCase

WorkItem
  ├── Feature
  └── Bug

SystemComponent
  ├── Microservice
  └── Database
```

---

## 属性定义

### 对象属性（Object Properties）

| 属性名 | Domain | Range | 含义 | 公理 |
|--------|--------|-------|------|------|
| assignedTo | WorkItem | Person | 工作项指派给某人 | — |
| resolves | Commit | Bug | 某次提交修复了某 Bug | — |
| implements | SourceCode | RequirementDoc | 代码实现了某需求 | — |
| tests | TestCase | SourceCode | 测试用例覆盖某段代码 | — |
| dependsOn | Microservice | Microservice | 微服务依赖另一微服务 | **Transitive** |
| author | Commit | Developer | 提交的作者 | Exactly 1 |

### 数据属性（Datatype Properties）

| 属性名 | Domain | 值类型 | 示例 |
|--------|--------|--------|------|
| hasStatus | WorkItem | xsd:string | "Open" / "Closed" |
| hasPriority | WorkItem | xsd:integer | 1（高）/ 2（中）/ 3（低）|
| createdAt | Commit | xsd:dateTime | "2026-04-23T10:30:00" |

---

## 公理（Axioms）

```
互斥：Bug ⊓ Feature = ∅
传递：dependsOn 是传递性属性（A→B, B→C ⇒ A→C）
基数：author 恰好为 1（owl:exactCardinality 1）
```

---

## Turtle 序列化文件（.ttl）

```turtle
# ── 命名空间 ──────────────────────────────────────────────
@prefix se:   <http://example.org/software-engineering#> .
@prefix rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl:  <http://www.w3.org/2002/07/owl#> .
@prefix xsd:  <http://www.w3.org/2001/XMLSchema#> .

# ── T-Box：类 ─────────────────────────────────────────────
se:Person       rdf:type owl:Class .
se:Developer    rdf:type owl:Class ; rdfs:subClassOf se:Person .
se:Tester       rdf:type owl:Class ; rdfs:subClassOf se:Person .

se:WorkItem     rdf:type owl:Class .
se:Bug          rdf:type owl:Class ; rdfs:subClassOf se:WorkItem .
se:Feature      rdf:type owl:Class ; rdfs:subClassOf se:WorkItem .

se:Artifact     rdf:type owl:Class .
se:Commit       rdf:type owl:Class ; rdfs:subClassOf se:Artifact .

se:Microservice rdf:type owl:Class .

# ── T-Box：互斥公理 ───────────────────────────────────────
[ rdf:type owl:AllDisjointClasses ;
  owl:members ( se:Bug se:Feature ) ] .

# ── T-Box：对象属性 ───────────────────────────────────────
se:assignedTo   rdf:type owl:ObjectProperty ;
                rdfs:domain se:WorkItem ;
                rdfs:range  se:Person .

se:resolves     rdf:type owl:ObjectProperty ;
                rdfs:domain se:Commit ;
                rdfs:range  se:Bug .

se:author       rdf:type owl:ObjectProperty ;
                rdfs:domain se:Commit ;
                rdfs:range  se:Developer ;
                owl:minCardinality 1 ;
                owl:maxCardinality 1 .

se:dependsOn    rdf:type owl:TransitiveProperty ;
                rdfs:domain se:Microservice ;
                rdfs:range  se:Microservice .

# ── T-Box：数据属性 ───────────────────────────────────────
se:hasStatus    rdf:type owl:DatatypeProperty ;
                rdfs:domain se:WorkItem ;
                rdfs:range  xsd:string .

se:hasPriority  rdf:type owl:DatatypeProperty ;
                rdfs:domain se:WorkItem ;
                rdfs:range  xsd:integer .

# ── A-Box：实例 ───────────────────────────────────────────
se:ZhangSan       rdf:type se:Developer .

se:Jira_99        rdf:type se:Bug ;
                  se:assignedTo  se:ZhangSan ;
                  se:hasStatus   "Open" ;
                  se:hasPriority 1 .

se:Commit_a1b2    rdf:type se:Commit ;
                  se:author   se:ZhangSan ;
                  se:resolves se:Jira_99 .

se:UserService    rdf:type se:Microservice .
se:PaymentService rdf:type se:Microservice ;
                  se:dependsOn se:UserService .
se:OrderService   rdf:type se:Microservice ;
                  se:dependsOn se:PaymentService .
# 推理机自动推导：OrderService dependsOn UserService
```

---

## SPARQL 查询示例

**CQ1：是谁的提交导致了 Bug-99？**
```sparql
SELECT ?developer WHERE {
  ?commit se:resolves se:Jira_99 .
  ?commit se:author   ?developer .
}
```

**CQ3：User Service 宕机影响哪些服务？（传递性自动展开）**
```sparql
SELECT ?affected WHERE {
  ?affected se:dependsOn se:UserService .
}
# 自动返回：PaymentService、OrderService（无需手写递归）
```

**CQ2：某需求是否有测试覆盖？**
```sparql
ASK {
  ?code se:implements se:Req_001 .
  ?test se:tests      ?code .
}
```
