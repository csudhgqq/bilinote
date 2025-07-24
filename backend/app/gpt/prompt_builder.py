from app.gpt.prompt import BASE_PROMPT

note_formats = [
    {'label': '目录', 'value': 'toc'},
    {'label': '原片跳转', 'value': 'link'},
    {'label': '原片截图', 'value': 'screenshot'},
    {'label': 'AI总结', 'value': 'summary'}
]

note_styles = [
    {'label': '精简', 'value': 'minimal'},
    {'label': '详细', 'value': 'detailed'},
    {'label': '学术', 'value': 'academic'},
    {"label": '教程',"value": 'tutorial', },
    {'label': '小红书', 'value': 'xiaohongshu'},
    {'label': '生活向', 'value': 'life_journal'},
    {'label': '任务导向', 'value': 'task_oriented'},
    {'label': '商业风格', 'value': 'business'},
    {'label': '会议纪要', 'value': 'meeting_minutes'},
    {'label': '游戏Wiki', 'value': 'game_wiki'}
]


# 生成 BASE_PROMPT 函数
def generate_base_prompt(title, segment_text, tags, _format=None, style=None, extras=None):
    # 生成 Base Prompt 开头部分
    prompt = BASE_PROMPT.format(
        video_title=title,
        segment_text=segment_text,
        tags=tags
    )

    # 添加用户选择的格式
    if _format:
        prompt += "\n" + "\n".join([get_format_function(f, style) for f in _format])

    # 根据用户选择的笔记风格添加描述
    if style:
        prompt += "\n" + get_style_format(style)

    # 添加额外内容
    if extras:
        prompt += f"\n{extras}"
    return prompt


# 获取格式函数
def get_format_function(format_type, style=None):
    format_map = {
        'toc': get_toc_format,
        'link': get_link_format,
        'screenshot': get_screenshot_format,
        'summary': lambda: get_summary_format(style)
    }
    return format_map.get(format_type, lambda: '')()


# 风格描述的处理
def get_style_format(style):
    style_map = {
        'minimal': '1. **精简信息**: 仅记录最重要的内容，简洁明了。',
        'detailed': '2. **详细记录**: 包含完整的内容和每个部分的详细讨论。需要尽可能多的记录视频内容，最好详细的笔记',
        'academic': '3. **学术风格**: 适合学术报告，正式且结构化。',
        'xiaohongshu': '''4. **小红书风格**: 
### 擅长使用下面的爆款关键词：
好用到哭，大数据，教科书般，小白必看，宝藏，绝绝子神器，都给我冲,划重点，笑不活了，YYDS，秘方，我不允许，压箱底，建议收藏，停止摆烂，上天在提醒你，挑战全网，手把手，揭秘，普通女生，沉浸式，有手就能做吹爆，好用哭了，搞钱必看，狠狠搞钱，打工人，吐血整理，家人们，隐藏，高级感，治愈，破防了，万万没想到，爆款，永远可以相信被夸爆手残党必备，正确姿势

### 采用二极管标题法创作标题：
- 正面刺激法:产品或方法+只需1秒 (短期)+便可开挂（逆天效果）
- 负面刺激法:你不XXX+绝对会后悔 (天大损失) +(紧迫感)
利用人们厌恶损失和负面偏误的心理

### 写作技巧
1. 使用惊叹号、省略号等标点符号增强表达力，营造紧迫感和惊喜感。
2. **使用emoji表情符号，来增加文字的活力**
3. 采用具有挑战性和悬念的表述，引发读、"无敌者好奇心，例如"暴涨词汇量"了"、"拒绝焦虑"等
4. 利用正面刺激和负面激，诱发读者的本能需求和动物基本驱动力，如"离离原上谱"、"你不知道的项目其实很赚"等
5. 融入热点话题和实用工具，提高文章的实用性和时效性，如"2023年必知"、"chatGPT狂飙进行时"等
6. 描述具体的成果和效果，强调标题中的关键词，使其更具吸引力，例如"英语底子再差，搞清这些语法你也能拿130+"
7. 使用吸引人的标题：''',

        'life_journal': '5. **生活向**: 记录个人生活感悟，情感化表达。',
        'task_oriented': '6. **任务导向**: 强调任务、目标，适合工作和待办事项。',
        'business': '7. **商业风格**: 适合商业报告、会议纪要，正式且精准。',
        'meeting_minutes': '8. **会议纪要**: 适合商业报告、会议纪要，正式且精准。',
        "tutorial":"9.**教程笔记**:尽可能详细的记录教程,特别是关键点和一些重要的结论步骤",
        'game_wiki': '''10. **游戏Wiki风格**: 
你需要按照以下DSL结构化数据模型来分析和记录游戏内容：

### 🎮 游戏基础信息 (Game Analysis Entry)
```yaml
游戏标识:
  - analysis_id: "GAME-{YYYYMMDD}-{序号}"
  - 分析时间戳: {当前时间}
  - 置信度评分: [0-1]
  
游戏分类:
  - 主要类型: "{主要游戏类型}"
  - 子类型: ["{子类型1}", "{子类型2}"]
  - 玩法标签: ["{标签1}", "{标签2}", "{标签3}"]
```

### 🔧 核心游戏系统 (Core Game Systems)
为每个识别到的游戏系统创建以下结构：

```yaml
系统名称: "{系统名称}"
系统类别: "{progression|combat|economy|narrative}"
复杂度评级: [1-5]
创新水平: [1-5]
玩家代理度: [1-5]

系统机制:
  - 机制名称: "{具体机制名}"
  - 触发条件: "{如何触发}"
  - 效果描述: "{具体效果}"
  - 稀有度: "{common|rare|epic|legendary}"
  - 威力等级: [1-10]
  - 协同潜力: [1-10]
  
平衡因素:
  - 成本: ["{需要消耗什么}"]
  - 限制: ["{有什么限制}"]  
  - 反制方法: ["{如何应对}"]
```

### 🏆 胜利条件系统 (Victory Conditions)
```yaml
胜利方式:
  - 条件ID: "{唯一标识}"
  - 描述: "{获胜方式}"
  - 类型: "{elimination|objective|survival|score}"
  - 要求: ["{具体要求}"]
  - 替代路径: ["{其他达成方式}"]
```

### 📈 进展机制 (Progression Mechanics)
```yaml
进展系统:
  - 系统名称: "{进展系统名}"
  - 类别: "{character|equipment|skill|unlock}"
  - 阶段: ["{阶段1}", "{阶段2}"]
  - 解锁条件: ["{解锁要求}"]
  - 奖励: ["{获得什么}"]
  - 永久升级: {是否永久}
  - 重置频率: "{never|run|session|periodic}"
```

### 🎨 设计影响分析 (Design Influences)
```yaml
影响来源:
  - 影响ID: "{来源游戏}_influence"
  - 来源游戏: "{参考的游戏}"
  - 影响类型: "{mechanical|aesthetic|narrative|ui_ux}"
  - 继承元素: ["{借鉴的元素}"]
  - 适应方式: "{如何改编}"
  - 创新添加: "{增加了什么新元素}"
  - 相似度评分: [0-1]
  - 影响权重: [0-1]
```

### 💡 创新因素 (Innovation Factors)
```yaml
创新点:
  - 创新名称: "{创新内容}"
  - 创新类别: "{gameplay|technology|narrative|social}"
  - 创新描述: "{详细说明}"
  - 市场影响: "{对行业的影响}"
  - 实现难度: [1-5]
```

### 📋 内容输出要求
1. **结构化输出**: 使用上述YAML格式清晰组织信息
2. **详细分析**: 深入分析每个游戏机制和系统
3. **数据完整**: 尽可能填写所有字段，缺失信息用"未知"标注
4. **客观评价**: 基于视频内容进行客观的数值评估
5. **系统关联**: 分析不同系统之间的相互关系和影响
6. **设计模式**: 识别和记录独特的设计模式和创新点

### 🎯 特别关注
- 游戏机制的创新性和独特性
- 玩家互动和反馈循环
- 平衡性设计和调整机制
- 与其他游戏的比较和影响关系
- 游戏设计趋势和模式识别

请严格按照此DSL结构分析游戏内容，确保输出的游戏Wiki条目具有高度的结构化和可检索性。'''
    }
    return style_map.get(style, '')


# 格式化输出内容
def get_toc_format():
    return '''
    9. **目录**: 自动生成一个基于 `##` 级标题的目录。不需要插入原片跳转
    '''


def get_link_format():
    return '''
    10. **原片跳转**: 为每个主要章节添加时间戳，使用格式 `*Content-[mm:ss]`。 
    重要：**始终**在章节标题前加上 `*Content` 前缀，例如：`AI 的发展史 *Content-[01:23]`。一定是标题在前 插入标记在后
    '''


def get_screenshot_format():
    return '''
11. **原片截图**:你收到的截图一般是一个网格，网格的每张图片就是一个时间点，左上角会包含时间mm:ss的格式，请你结合我发你的图片插入截图提示，请你帮助用户更好的理解视频内容，请你认真的分析每个图片和对应的转写文案，插入最合适的内容来备注用户理解，请一定按照这个格式 返回否则系统无法解析：
- 格式：`*Screenshot-[mm:ss]`

    '''


def get_summary_format(style=None):
    if style == 'game_wiki':
        return '''
    12. **游戏Wiki AI总结**: 在笔记末尾必须包含以下结构化总结（使用二级标题 ## AI 总结）：
    
    **必须包含以下内容：**
    - **🎮 游戏类型**: 明确标识主要游戏类型和子类型（如：roguelike, bullet heaven, 策略等）
    - **🏷️ 玩法标签**: 列出3-5个核心玩法标签（如：自动战斗, 装备收集, 角色升级等）
    - **🔥 核心亮点**: 游戏最突出的创新点或特色机制
    - **📊 复杂度评估**: 简要评估游戏的学习难度和深度
    - **🎯 目标群体**: 适合的玩家类型
    
    **格式示例：**
    ```
    ## AI 总结
    
    **🎮 游戏类型**: Chess Roguelike / Bullet Heaven
    **🏷️ 玩法标签**: 自动战斗, 棋子升级, 遗物收集, 回合策略, Boss挑战
    **🔥 核心亮点**: 独创的象棋机制与roguelike元素融合
    **📊 复杂度评估**: 中等复杂度，易上手难精通
    **🎯 目标群体**: 策略游戏爱好者、roguelike玩家
    ```
    '''
    else:
        return '''
    12. **AI总结**: 在笔记末尾加入简短的AI生成总结,并且二级标题 就是 AI 总结 例如 ## AI 总结。
    '''
