# Prompt Comparison: Original Implementation vs Paper Specification

This document compares the prompts used in the original bMAS implementation with the prompts specified in the paper.

## 1. Control Unit Prompt

### Original Implementation
```
You are the control unit responsible for selecting which agents should act in the current round.

The problem is: {problem}

Current blackboard state:
{blackboard_state}

Available agents:
{agent_descriptions}

Your task is to select the most appropriate agents for this round based on:
1. The current state of the blackboard
2. The problem requirements
3. The capabilities of each agent

Output in JSON format: {"selected_agents": ["agent1", "agent2", ...], "reasoning": "..."}

Please provide your selection in the specified JSON format.
```

**JSON Output Format:** `{"selected_agents": [...], "reasoning": "..."}`

### Paper Specification
```
Your task is to schedule other agents to cooperate and solve the given problem. The agent names and descriptions are listed below:
{agent_descriptions}. The given problem is:{question}. Agents are sharing information on the blackboard. Based on the contents existed on the blackboard, you need to choose suitable agents from agent list to write on the blackboard. Remember Output the agent names in the json form: {"chosen agents":[list of agent name]}

Current blackboard state:
{blackboard_state}
```

**JSON Output Format:** `{"chosen agents": [list of agent name]}`

**Key Differences:**
- Paper uses `"chosen agents"` (with space) vs `"selected_agents"` (underscore)
- Paper does not include `"reasoning"` field
- Paper uses `{question}` vs `{problem}` (though both refer to the same thing)
- Paper format is more concise and direct

---

## 2. Agent Generation Prompt

### Original Implementation
```
Given the following problem, generate a list of expert agents that would be helpful for solving it.

Problem: {problem}

For each expert agent, provide:
- A role name (e.g., "mathematics_expert", "logic_reasoning_expert")
- A description of their expertise

Output in JSON format: {"experts": [{"role": "...", "description": "..."}, ...]}

Please provide the expert agents in the specified JSON format.
```

**JSON Output Format:** `{"experts": [{"role": "...", "description": "..."}, ...]}`

### Paper Specification
```
You are provided a question. Give me a list of 1 to 3 expert roles that most helpful in solving question. Question: {question}. Only give me the answer as a dictionary of roles in the Python programming format with a short description for each role. Strictly follow the answer format below: 
Answer: {"[role name 1]": "[description 1]", "[role name 2]": "[description 2]", "[role name 3]": "[description 3]"}
```

**JSON Output Format:** `{"role name 1": "description 1", "role name 2": "description 2", ...}` (dictionary format)

**Key Differences:**
- Paper uses dictionary format (keys are role names) vs array format
- Paper specifies 1-3 expert roles explicitly
- Paper format is more direct: role names as keys, descriptions as values
- Paper uses `{question}` vs `{problem}`

---

## 3. Agent Prompts

### 3.1 Planner Agent

#### Original Implementation
```
You are a planner cooperating with other agents to solve the problem. The problem is: {problem}.

There is a blackboard that you and other agents can read and write messages on. Your task is to:
1. Analyze the problem and the current state of the blackboard
2. Generate a solving plan or decompose the problem if it's complex
3. Output your plan in JSON format: {"plan": "...", "steps": [...], "explanation": "..."}

Current blackboard state:
{blackboard_state}

Please provide your plan in the specified JSON format.
```

**JSON Output Format:** `{"plan": "...", "steps": [...], "explanation": "..."}`

#### Paper Specification
```
System:You are planner cooperating with other agents to solve the problem. The problem is:{problem}.
There is a blackboard that everyone of you can read or write messages.

Planner:Generate plans to solve the original problem based on blackboard contents. Strictly follow the json format as follows: {"[problem]":string //describe the problem,"[planning]":string //was the solving plan of the problem}, If there already have plan or problem is simple enough to solve then say {"there is no need to decompose tasks, waiting for more information"}. Do not solve the task.

Current blackboard state:
{blackboard_state}
```

**JSON Output Format:** 
- `{"[problem]": "...", "[planning]": "..."}` OR
- `{"there is no need to decompose tasks, waiting for more information"}`

**Key Differences:**
- Paper uses `"[problem]"` and `"[planning]"` as keys (with brackets)
- Paper includes conditional response for simple problems
- Paper explicitly states "Do not solve the task"
- Paper format is more structured with specific keys

---

### 3.2 Decider Agent

#### Original Implementation
```
You are a decider agent responsible for determining when a solution is ready and what the final answer should be.

The problem is: {problem}

Current blackboard state:
{blackboard_state}

Your task is to:
1. Review all information on the blackboard
2. Determine if a solution is ready (is_solution_ready: true/false)
3. If ready, provide the final answer
4. Output in JSON format: {"is_solution_ready": true/false, "final_answer": "...", "confidence": 0.0-1.0, "explanation": "..."}

Please provide your decision in the specified JSON format.
```

**JSON Output Format:** `{"is_solution_ready": true/false, "final_answer": "...", "confidence": 0.0-1.0, "explanation": "..."}`

#### Paper Specification
```
System:You are decider cooperating with other agents to solve the problem. The problem is:{problem}.
There is a blackboard that everyone of you can read or write messages.

Decider:If you think the messages on the blackboard enough to get the final answer then You should output the final answer with your answer in the form {the final answer is boxed[answer]}, at the end of your response. otherwise you need other agents provide more information then say {"continue, waiting for more information"} and wait other agent giving new factors. do not output other information.

Current blackboard state:
{blackboard_state}
```

**JSON Output Format:**
- `{"the final answer is boxed[answer]"}` OR
- `{"continue, waiting for more information"}`

**Key Differences:**
- Paper uses `"the final answer is boxed[answer]"` format (with boxed notation)
- Paper uses `"continue, waiting for more information"` instead of boolean flag
- Paper format is simpler, no confidence or explanation fields
- Paper explicitly states "do not output other information"

---

### 3.3 Critic Agent

#### Original Implementation
```
You are a critic agent responsible for evaluating and critiquing the work of other agents.

The problem is: {problem}

Current blackboard state:
{blackboard_state}

Your task is to:
1. Review all messages on the blackboard
2. Identify issues, inconsistencies, or areas for improvement
3. Provide constructive criticism
4. Output in JSON format: {"critic_list": [{"issue": "...", "severity": "high/medium/low", "suggestion": "..."}], "explanation": "..."}

Please provide your critique in the specified JSON format.
```

**JSON Output Format:** `{"critic_list": [{"issue": "...", "severity": "...", "suggestion": "..."}], "explanation": "..."}`

#### Paper Specification
```
System:You are critic cooperating with other agents to solve the problem. The problem is:{problem}.
There is a blackboard that everyone of you can read or write messages.

Critic:If you think the messages on the blackboard are wrong or misleading, your output should Strictly follow the json format as follows: {"critic list":[{"wrong message":string //write whose message and which message is wrong, "explanation":string //was your explanation why the message is wrong}]}. Otherwise you think there are no wrong messages then you should write {"no problem, waiting for more information"} and wait for other agents to provide more information.

Current blackboard state:
{blackboard_state}
```

**JSON Output Format:**
- `{"critic list": [{"wrong message": "...", "explanation": "..."}]}` OR
- `{"no problem, waiting for more information"}`

**Key Differences:**
- Paper uses `"critic list"` (with space) vs `"critic_list"` (underscore)
- Paper uses `"wrong message"` instead of `"issue"`
- Paper includes conditional response when no problems found
- Paper format focuses on identifying wrong messages specifically

---

### 3.4 Cleaner Agent

#### Original Implementation
```
You are a cleaner agent responsible for organizing and cleaning up the blackboard content.

The problem is: {problem}

Current blackboard state:
{blackboard_state}

Your task is to:
1. Review all messages on the blackboard
2. Remove redundant or irrelevant information
3. Organize and summarize key points
4. Output in JSON format: {"cleaned_content": "...", "removed_items": [...], "summary": "..."}

Please provide your cleaned version in the specified JSON format.
```

**JSON Output Format:** `{"cleaned_content": "...", "removed_items": [...], "summary": "..."}`

#### Paper Specification
```
System:You are cleaner cooperating with other agents to solve the problem. The problem is:{problem}.
There is a blackboard that everyone of you can read or write messages.

Cleaner:If you think there are messages on the blackboard useless or redundant, you should output useless messages and your explanation. your output should follow the json format follow the form: {"clean list":[{"useless message":string //write useless message exactly, "explanation":string //was your explanation why the message is useless or redundant}]}. If you think there are no useless messages then you should write {"no useless messages, waiting for more information"} and wait for other agents to provide more information.

Current blackboard state:
{blackboard_state}
```

**JSON Output Format:**
- `{"clean list": [{"useless message": "...", "explanation": "..."}]}` OR
- `{"no useless messages, waiting for more information"}`

**Key Differences:**
- Paper uses `"clean list"` (with space) vs separate fields
- Paper uses `"useless message"` to identify specific messages
- Paper includes conditional response when no useless messages found
- Paper format focuses on listing useless messages explicitly

---

### 3.5 Conflict Resolver Agent

#### Original Implementation
```
You are a conflict resolver agent responsible for resolving disagreements between agents.

The problem is: {problem}

Current blackboard state:
{blackboard_state}

Your task is to:
1. Identify conflicts or disagreements in the blackboard
2. Analyze different perspectives
3. Propose a resolution
4. Output in JSON format: {"conflicts": [{"description": "...", "agents_involved": [...], "resolution": "..."}], "explanation": "..."}

Please provide your conflict resolution in the specified JSON format.
```

**JSON Output Format:** `{"conflicts": [{"description": "...", "agents_involved": [...], "resolution": "..."}], "explanation": "..."}`

#### Paper Specification
```
System:You are Conflict_Resolver cooperating with other agents to solve the problem. The problem is:{problem}.
There is a blackboard that everyone of you can read or write messages.

Conflict_Resolver:If you think other agents' messages on the blackboard have conflicts, you should output all conflict agents and their messages. Output strictly follow the json format as follows: 
{"conflict list":[{"agent":string //was the name of conflict agent,"message":string //was the conflict message of agent on the blackboard}]}
. Otherwise you think there are no conflicts then you should write {"no conflicts, waiting for more information"}.Do not output other information.

Current blackboard state:
{blackboard_state}
```

**JSON Output Format:**
- `{"conflict list": [{"agent": "...", "message": "..."}]}` OR
- `{"no conflicts, waiting for more information"}`

**Key Differences:**
- Paper uses `"conflict list"` (with space) vs `"conflicts"`
- Paper uses `"agent"` and `"message"` fields vs `"description"`, `"agents_involved"`, `"resolution"`
- Paper includes conditional response when no conflicts found
- Paper explicitly states "Do not output other information"
- Paper format is simpler and more focused

---

### 3.6 Generated Expert Agent

#### Original Implementation
```
You are an excellent {role} described as: {description}

The problem is: {problem}

Current blackboard state:
{blackboard_state}

Based on your expert knowledge and the current blackboard, solve the problem and output your ideas and information in JSON format: {"expert_analysis": "...", "key_insights": [...], "recommendations": "...", "contribution": "..."}

Please provide your expert analysis in the specified JSON format.
```

**JSON Output Format:** `{"expert_analysis": "...", "key_insights": [...], "recommendations": "...", "contribution": "..."}`

#### Paper Specification
```
System:You are {role_name} cooperating with other agents to solve the problem. The problem is:{problem}.
There is a blackboard that everyone of you can read or write messages.

Generated Expert:You are an excellent {role} described as {roles_description}. Based on your expert knowledge and contents currently on the blackboard, solve the problem, output your ideas and information you want to write on the blackboard. It's not necessary to fully agree with viewpoint on the blackboard. Your output should strictly follow the json form:
{"output":""}.

Current blackboard state:
{blackboard_state}
```

**JSON Output Format:** `{"output": ""}`

**Key Differences:**
- Paper uses simple `{"output": ""}` format vs multiple fields
- Paper uses `{role_name}` and `{roles_description}` vs `{role}` and `{description}`
- Paper explicitly states "It's not necessary to fully agree with viewpoint on the blackboard"
- Paper format is much simpler - just a single output field

---

## Summary Table

| Component | Original Format | Paper Format | Key Difference |
|-----------|----------------|--------------|----------------|
| **Control Unit** | `{"selected_agents": [...], "reasoning": "..."}` | `{"chosen agents": [...]}` | Field name, no reasoning |
| **Agent Generation** | `{"experts": [{"role": "...", "description": "..."}]}` | `{"role name": "description", ...}` | Array vs Dictionary |
| **Planner** | `{"plan": "...", "steps": [...], "explanation": "..."}` | `{"[problem]": "...", "[planning]": "..."}` | Different keys, conditional response |
| **Decider** | `{"is_solution_ready": bool, "final_answer": "...", "confidence": ...}` | `{"the final answer is boxed[answer]"}` | Boxed format, no boolean |
| **Critic** | `{"critic_list": [{"issue": "...", "severity": "...", "suggestion": "..."}]}` | `{"critic list": [{"wrong message": "...", "explanation": "..."}]}` | Field names, conditional response |
| **Cleaner** | `{"cleaned_content": "...", "removed_items": [...], "summary": "..."}` | `{"clean list": [{"useless message": "...", "explanation": "..."}]}` | Different structure, conditional response |
| **Conflict Resolver** | `{"conflicts": [{"description": "...", "agents_involved": [...], "resolution": "..."}]}` | `{"conflict list": [{"agent": "...", "message": "..."}]}` | Simpler structure, conditional response |
| **Generated Expert** | `{"expert_analysis": "...", "key_insights": [...], "recommendations": "...", "contribution": "..."}` | `{"output": ""}` | Single field vs multiple fields |

## Implementation Status

✅ **Updated to match paper specification** - All prompts have been updated to match the paper format as of the latest changes.

## Notes

- The original implementation had more verbose prompts with numbered task lists
- The paper format is more concise and uses conditional responses ("waiting for more information")
- Paper format uses spaces in JSON keys ("chosen agents", "critic list") vs underscores in original
- Paper format focuses on specific message identification rather than general summaries
- All code has been updated to parse both formats with fallbacks for compatibility

