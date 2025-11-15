"""
Visualization utility for experiment traces.
Creates visual representations of agent execution flows.
"""
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
import sys
import io


def visualize_flow(trace_file: str, output_file: Optional[str] = None):
    """
    Create a visual representation of the agent execution flow.
    
    Args:
        trace_file: Path to trace JSON file
        output_file: Optional output file path (default: trace_file with .txt extension)
    """
    with open(trace_file, 'r', encoding='utf-8') as f:
        trace = json.load(f)
    
    lines = []
    lines.append("="*80)
    lines.append("AGENT EXECUTION FLOW VISUALIZATION")
    lines.append("="*80)
    lines.append(f"\nProblem: {trace['problem']}")
    if trace.get('ground_truth'):
        lines.append(f"Ground Truth: {trace['ground_truth']}")
    lines.append(f"Final Answer: {trace.get('final_answer', 'N/A')}")
    lines.append("")
    
    # Agent pool
    lines.append("-"*80)
    lines.append("AGENT POOL")
    lines.append("-"*80)
    for agent in trace.get('agent_pool', []):
        agent_type = agent.get('type', 'unknown').upper()
        lines.append(f"  {agent['name']} ({agent['role']}) [{agent_type}]")
    lines.append("")
    
    # Round-by-round flow
    lines.append("="*80)
    lines.append("EXECUTION FLOW")
    lines.append("="*80)
    
    for round_entry in trace.get('rounds', []):
        round_num = round_entry.get('round', 0)
        lines.append(f"\n{'='*80}")
        lines.append(f"ROUND {round_num}")
        lines.append(f"{'='*80}")
        
        # Agent selection
        selected = round_entry.get('selected_agents', [])
        lines.append(f"\n[CONTROL UNIT] Selected Agents: {', '.join(selected)}")
        if 'selection_reasoning' in round_entry:
            reasoning = round_entry['selection_reasoning'][:200]
            lines.append(f"  Reasoning: {reasoning}...")
        
        # Agent actions
        lines.append(f"\n[AGENT ACTIONS]")
        for action in round_entry.get('agent_actions', []):
            agent_name = action.get('agent', 'unknown')
            result = action.get('result', {})
            
            lines.append(f"\n  -> {agent_name.upper()}")
            
            # Show response preview
            raw_response = result.get('raw_response', '')
            if raw_response:
                preview = raw_response[:300].replace('\n', ' ')
                lines.append(f"     Response: {preview}...")
            
            # Show parsed response if available
            parsed = result.get('response', {})
            if parsed and isinstance(parsed, dict):
                if 'plan' in parsed:
                    lines.append(f"     Plan: {parsed['plan'][:200]}...")
                if 'final_answer' in parsed:
                    lines.append(f"     Final Answer: {parsed['final_answer']}")
                if 'is_solution_ready' in parsed:
                    lines.append(f"     Solution Ready: {parsed['is_solution_ready']}")
            
            # Show tokens
            tokens = result.get('tokens', 0)
            if tokens:
                lines.append(f"     Tokens: {tokens}")
        
        # Blackboard snapshot summary
        if 'blackboard_snapshot' in round_entry:
            snapshot = round_entry['blackboard_snapshot']
            public_count = len(snapshot.get('public_messages', []))
            private_count = len(snapshot.get('private_spaces', {}))
            lines.append(f"\n[BLACKBOARD] {public_count} public messages, {private_count} private spaces")
    
    lines.append("\n" + "="*80)
    lines.append("END OF FLOW")
    lines.append("="*80)
    
    output = "\n".join(lines)
    
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"Flow visualization saved to: {output_file}")
    else:
        # Handle Unicode encoding for Windows console
        import sys
        import io
        if sys.stdout.encoding != 'utf-8':
            try:
                sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
            except:
                pass
        print(output)
    
    return output


def create_ascii_diagram(trace_file: str):
    """
    Create an ASCII art diagram of the agent flow.
    
    Args:
        trace_file: Path to trace JSON file
    """
    with open(trace_file, 'r', encoding='utf-8') as f:
        trace = json.load(f)
    
    lines = []
    lines.append("\n" + "="*80)
    lines.append("AGENT FLOW DIAGRAM")
    lines.append("="*80 + "\n")
    
    for round_entry in trace.get('rounds', []):
        round_num = round_entry.get('round', 0)
        selected = round_entry.get('selected_agents', [])
        
        lines.append(f"Round {round_num}:")
        lines.append("  [Control Unit]")
        lines.append("       |")
        lines.append("       v")
        lines.append("  Selected: " + ", ".join(selected))
        lines.append("       |")
        lines.append("       v")
        
        # Show agent execution
        for i, action in enumerate(round_entry.get('agent_actions', [])):
            agent_name = action.get('agent', 'unknown')
            connector = "  |--->" if i < len(round_entry.get('agent_actions', [])) - 1 else "  `--->"
            lines.append(f"{connector} [{agent_name}]")
            
            # Show if solution ready
            result = action.get('result', {})
            parsed = result.get('response', {})
            if isinstance(parsed, dict) and parsed.get('is_solution_ready'):
                lines.append("       |")
                lines.append("       v")
                lines.append("  [SOLUTION READY]")
        
        lines.append("       |")
        lines.append("       v")
        lines.append("  [Blackboard Updated]")
        lines.append("")
    
    lines.append("="*80)
    
    output = "\n".join(lines)
    # Handle Unicode encoding for Windows console
    import sys
    import io
    if sys.stdout.encoding != 'utf-8':
        try:
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        except:
            pass
    print(output)
    return output


def create_paper_style_diagram(trace_file1: str, trace_file2: Optional[str] = None, 
                               output_image: Optional[str] = None, figsize: tuple = (20, 12)):
    """
    Create a paper-style visualization matching the authors' illustration method.
    Shows side-by-side comparison with vertical flow diagrams and agent contributions.
    
    Args:
        trace_file1: Path to first trace JSON file
        trace_file2: Optional path to second trace JSON file (for comparison)
        output_image: Optional output image file path
        figsize: Figure size tuple (width, height) in inches
    """
    try:
        import matplotlib.pyplot as plt
        import matplotlib.patches as mpatches
        from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle
        from matplotlib import font_manager
    except ImportError:
        print("Error: matplotlib is required for image generation.")
        print("Install it with: pip install matplotlib")
        return None
    
    # Load traces
    with open(trace_file1, 'r', encoding='utf-8') as f:
        trace1 = json.load(f)
    
    trace2 = None
    if trace_file2:
        with open(trace_file2, 'r', encoding='utf-8') as f:
            trace2 = json.load(f)
    
    # Determine output filename
    if output_image is None:
        if trace2:
            output_image = str(Path(trace_file1).parent / "paper_style_comparison.png")
        else:
            output_image = str(Path(trace_file1).with_suffix('.png'))
    
    # Paper-style color scheme (matching the illustration)
    color_map = {
        'planner': '#90EE90',        # Light Green (like in paper)
        'decider': '#FFD700',        # Yellow/Gold
        'critic': '#FF6B6B',         # Red
        'cleaner': '#D3D3D3',        # Light Gray
        'conflict_resolver': '#9370DB',  # Purple
        'expert': '#4A90E2',         # Blue (for all expert agents)
        'default': '#95A5A6'        # Gray
    }
    
    # Create figure
    fig = plt.figure(figsize=figsize, facecolor='white')
    
    if trace2:
        # Side-by-side layout
        gs = fig.add_gridspec(1, 3, width_ratios=[1, 0.15, 1], hspace=0.3, wspace=0.1)
        ax1 = fig.add_subplot(gs[0, 0])
        ax_legend = fig.add_subplot(gs[0, 1])
        ax2 = fig.add_subplot(gs[0, 2])
    else:
        # Single trace layout
        gs = fig.add_gridspec(1, 2, width_ratios=[1, 0.15], hspace=0.3, wspace=0.1)
        ax1 = fig.add_subplot(gs[0, 0])
        ax_legend = fig.add_subplot(gs[0, 1])
        ax2 = None
    
    # Helper function to get agent color
    def get_agent_color(agent_name: str, agent_role: str = None) -> str:
        name_lower = agent_name.lower()
        role_lower = (agent_role or "").lower()
        
        if 'planner' in name_lower or 'planner' in role_lower:
            return color_map['planner']
        elif 'decider' in name_lower or 'decider' in role_lower:
            return color_map['decider']
        elif 'critic' in name_lower or 'critic' in role_lower:
            return color_map['critic']
        elif 'cleaner' in name_lower or 'cleaner' in role_lower:
            return color_map['cleaner']
        elif 'conflict' in name_lower:
            return color_map['conflict_resolver']
        elif 'expert' in name_lower or agent_name.startswith('expert_'):
            return color_map['expert']
        else:
            return color_map['default']
    
    # Helper function to get display name
    def get_display_name(agent_name: str) -> str:
        # Remove 'expert_' prefix and format nicely
        name = agent_name.replace('expert_', '').replace('_', ' ')
        # Capitalize properly
        parts = name.split()
        return ' '.join([p.capitalize() for p in parts])
    
    # Helper function to draw a trace
    def draw_trace(ax, trace, is_left: bool = True):
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        
        # Problem text at top
        problem = trace.get('problem') or 'Unknown Problem'
        if len(problem) > 120:
            problem = problem[:117] + "..."
        
        problem_text = f"Q: {problem}"
        ax.text(0.5, 0.95, problem_text, ha='center', va='top', fontsize=10, 
                weight='bold', wrap=True, bbox=dict(boxstyle='round,pad=0.5', 
                facecolor='white', edgecolor='black', linewidth=1))
        
        # Get rounds
        rounds = trace.get('rounds', [])
        if not rounds:
            ax.text(0.5, 0.5, "No rounds found", ha='center', va='center', fontsize=12)
            return
        
        # Build agent flow structure
        agent_flow = []  # List of (round_idx, agent_name, agent_role, y_pos)
        round_agents = {}  # round_idx -> list of agents
        
        for round_idx, round_entry in enumerate(rounds):
            selected_agents = round_entry.get('selected_agents', [])
            agent_actions = round_entry.get('agent_actions', [])
            
            if not selected_agents and agent_actions:
                selected_agents = [action.get('agent', 'unknown') for action in agent_actions]
            
            round_agents[round_idx] = selected_agents
        
        # Calculate positions for flow diagram
        flow_start_y = 0.75
        flow_height = 0.15
        box_width = 0.12
        box_height = 0.04
        spacing = 0.02
        
        # Draw flow diagram (vertical)
        current_y = flow_start_y
        all_agents_drawn = []
        
        for round_idx, round_entry in enumerate(rounds):
            selected_agents = round_agents.get(round_idx, [])
            if not selected_agents:
                continue
            
            # Group agents by type for better layout
            expert_agents = [a for a in selected_agents if 'expert' in a.lower() or a.startswith('expert_')]
            predefined_agents = [a for a in selected_agents if a not in expert_agents]
            
            # Draw expert agents first (side by side)
            if expert_agents:
                num_experts = len(expert_agents)
                expert_width = min(box_width, 0.25 / num_experts)
                expert_start_x = 0.5 - (num_experts * expert_width + (num_experts - 1) * spacing) / 2
                
                for i, agent_name in enumerate(expert_agents):
                    x_pos = expert_start_x + i * (expert_width + spacing)
                    color = get_agent_color(agent_name)
                    display_name = get_display_name(agent_name)
                    
                    # Shorten name if needed
                    if len(display_name) > 12:
                        display_name = display_name[:10] + "..."
                    
                    box = FancyBboxPatch((x_pos, current_y - box_height), expert_width, box_height,
                                         boxstyle="round,pad=0.005", facecolor=color, 
                                         edgecolor='black', linewidth=1.2)
                    ax.add_patch(box)
                    ax.text(x_pos + expert_width/2, current_y - box_height/2, display_name,
                           ha='center', va='center', fontsize=7, weight='bold', wrap=True)
                    
                    all_agents_drawn.append((agent_name, current_y - box_height/2))
            
            # Draw predefined agents below experts
            if predefined_agents:
                predefined_y = current_y - box_height - spacing if expert_agents else current_y
                for agent_name in predefined_agents:
                    color = get_agent_color(agent_name)
                    display_name = get_display_name(agent_name)
                    
                    if len(display_name) > 12:
                        display_name = display_name[:10] + "..."
                    
                    box = FancyBboxPatch((0.5 - box_width/2, predefined_y - box_height), box_width, box_height,
                                         boxstyle="round,pad=0.005", facecolor=color,
                                         edgecolor='black', linewidth=1.2)
                    ax.add_patch(box)
                    ax.text(0.5, predefined_y - box_height/2, display_name,
                           ha='center', va='center', fontsize=7, weight='bold')
                    
                    all_agents_drawn.append((agent_name, predefined_y - box_height/2))
                    
                    # Check if solution ready
                    for action in round_entry.get('agent_actions', []):
                        if action.get('agent') == agent_name:
                            result = action.get('result', {})
                            parsed = result.get('response', {})
                            if isinstance(parsed, dict) and parsed.get('is_solution_ready'):
                                # Draw solution ready indicator
                                solution_box = FancyBboxPatch((0.5 - box_width/2, predefined_y - box_height - 0.03),
                                                              box_width, 0.02,
                                                              boxstyle="round,pad=0.002",
                                                              facecolor='#FFD700', edgecolor='black', linewidth=1.5)
                                ax.add_patch(solution_box)
                                ax.text(0.5, predefined_y - box_height - 0.02, "✓ Solution",
                                       ha='center', va='center', fontsize=6, weight='bold')
            
            # Update current_y for next round
            if expert_agents and predefined_agents:
                current_y = current_y - box_height * 2 - spacing * 2
            elif expert_agents or predefined_agents:
                current_y = current_y - box_height - spacing
            
            # Draw arrow to next round
            if round_idx < len(rounds) - 1:
                arrow = FancyArrowPatch((0.5, current_y - 0.01), (0.5, current_y - spacing),
                                        arrowstyle='->', mutation_scale=15, linewidth=1.5, color='gray')
                ax.add_patch(arrow)
        
        # Draw agent contributions text below diagram
        contributions_y = current_y - 0.1
        contributions_text = []
        
        for round_idx, round_entry in enumerate(rounds):
            for action in round_entry.get('agent_actions', []):
                agent_name = action.get('agent', 'unknown')
                result = action.get('result', {})
                parsed = result.get('response', {})
                raw_response = result.get('raw_response', '')
                
                # Extract key contribution
                display_name = get_display_name(agent_name)
                contribution = ""
                
                if isinstance(parsed, dict):
                    if 'final_answer' in parsed and parsed['final_answer']:
                        contribution = f"{display_name}: \"{parsed['final_answer']}\""
                    elif 'plan' in parsed:
                        plan_text = str(parsed['plan'])[:100]
                        contribution = f"{display_name}: {plan_text}..."
                    elif 'expert_analysis' in parsed:
                        analysis = str(parsed['expert_analysis'])[:100]
                        contribution = f"{display_name}: {analysis}..."
                
                if not contribution and raw_response:
                    contribution = f"{display_name}: {raw_response[:80]}..."
                
                if contribution:
                    contributions_text.append(contribution)
        
        # Display contributions
        if contributions_text:
            contributions_display = "\n".join(contributions_text[:6])  # Limit to 6 contributions
            ax.text(0.5, contributions_y, contributions_display, ha='center', va='top',
                   fontsize=7, wrap=True, bbox=dict(boxstyle='round,pad=0.3',
                   facecolor='#F5F5F5', edgecolor='gray', linewidth=0.5))
        
        # Final answer at bottom
        final_answer = trace.get('final_answer')
        if final_answer:
            ground_truth = trace.get('ground_truth')
            is_correct = trace.get('correct', False)
            
            answer_text = f"Final Answer: {final_answer}"
            if ground_truth:
                answer_text += f"\nGround Truth: {ground_truth}"
            if is_correct:
                answer_text += " ✓"
            
            ax.text(0.5, 0.05, answer_text, ha='center', va='bottom', fontsize=9,
                   weight='bold', bbox=dict(boxstyle='round,pad=0.3',
                   facecolor='#E8F5E9' if is_correct else '#FFEBEE',
                   edgecolor='green' if is_correct else 'red', linewidth=2))
    
    # Draw traces
    draw_trace(ax1, trace1, is_left=True)
    if trace2:
        draw_trace(ax2, trace2, is_left=False)
    
    # Draw legend in middle
    ax_legend.axis('off')
    ax_legend.set_xlim(0, 1)
    ax_legend.set_ylim(0, 1)
    
    legend_elements = [
        mpatches.Patch(facecolor=color_map['expert'], label='Expert Agents\n(Mathematician,\nData Analyst, etc.)'),
        mpatches.Patch(facecolor=color_map['planner'], label='Planner'),
        mpatches.Patch(facecolor=color_map['decider'], label='Decider'),
        mpatches.Patch(facecolor=color_map['cleaner'], label='Cleaner'),
        mpatches.Patch(facecolor=color_map['critic'], label='Critic'),
        mpatches.Patch(facecolor=color_map['conflict_resolver'], label='Conflict\nResolver'),
    ]
    
    ax_legend.legend(handles=legend_elements, loc='center', fontsize=8, frameon=False)
    
    # Save
    plt.savefig(output_image, dpi=200, bbox_inches='tight', facecolor='white', edgecolor='none')
    plt.close()
    
    print(f"Paper-style diagram saved to: {output_image}")
    return output_image


def create_image_diagram(trace_file: str, output_image: Optional[str] = None, figsize: tuple = (16, 10)):
    """
    Create a visual image diagram of the agent execution flow.
    
    Args:
        trace_file: Path to trace JSON file
        output_image: Optional output image file path (default: trace_file with .png extension)
        figsize: Figure size tuple (width, height) in inches
    """
    try:
        import matplotlib.pyplot as plt
        import matplotlib.patches as mpatches
        from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
        import matplotlib.patches as patches
    except ImportError:
        print("Error: matplotlib is required for image generation.")
        print("Install it with: pip install matplotlib")
        return None
    
    with open(trace_file, 'r', encoding='utf-8') as f:
        trace = json.load(f)
    
    # Determine output filename
    if output_image is None:
        output_image = str(Path(trace_file).with_suffix('.png'))
    
    # Color scheme for different agent types
    color_map = {
        'planner': '#4A90E2',      # Blue
        'decider': '#50C878',       # Green
        'critic': '#FF6B6B',        # Red
        'cleaner': '#FFA500',       # Orange
        'conflict_resolver': '#9B59B6',  # Purple
        'expert': '#2ECC71',        # Light Green
        'default': '#95A5A6'        # Gray
    }
    
    # Create figure
    fig, ax = plt.subplots(figsize=figsize)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # Title
    problem = trace.get('problem') or 'Unknown Problem'
    if problem and len(problem) > 80:
        problem = problem[:77] + "..."
    
    title = f"Agent Execution Flow\n{problem}"
    if trace.get('final_answer'):
        title += f"\nFinal Answer: {trace.get('final_answer', 'N/A')}"
    
    ax.text(5, 9.5, title, ha='center', va='top', fontsize=12, weight='bold',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    # Process rounds
    rounds = trace.get('rounds', [])
    if not rounds:
        ax.text(5, 5, "No rounds found in trace", ha='center', va='center', fontsize=14)
        plt.savefig(output_image, dpi=150, bbox_inches='tight')
        plt.close()
        print(f"Image saved to: {output_image}")
        return output_image
    
    # Calculate layout
    num_rounds = len(rounds)
    round_width = 8.0 / max(num_rounds, 1)
    start_x = 1.0
    
    y_positions = {}  # Track y positions for arrows
    current_y = 7.5
    
    # Draw rounds
    for round_idx, round_entry in enumerate(rounds):
        round_num = round_entry.get('round', round_idx + 1)
        round_x = start_x + round_idx * round_width
        
        # Round header
        round_label = f"Round {round_num}"
        ax.text(round_x + round_width/2, current_y + 0.3, round_label,
                ha='center', va='bottom', fontsize=11, weight='bold',
                bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.7))
        
        # Control Unit box
        control_y = current_y
        control_box = FancyBboxPatch((round_x, control_y - 0.2), round_width - 0.1, 0.15,
                                     boxstyle="round,pad=0.02", 
                                     facecolor='lightgray', edgecolor='black', linewidth=1.5)
        ax.add_patch(control_box)
        ax.text(round_x + round_width/2, control_y - 0.125, "Control Unit",
                ha='center', va='center', fontsize=9, weight='bold')
        
        # Selected agents
        selected_agents = round_entry.get('selected_agents', [])
        agent_actions = round_entry.get('agent_actions', [])
        
        if not selected_agents and agent_actions:
            # Extract agent names from actions if not in selected_agents
            selected_agents = [action.get('agent', 'unknown') for action in agent_actions]
        
        # Draw arrow from control unit to agents
        agent_start_y = control_y - 0.35
        
        # Draw agents
        num_agents = len(selected_agents)
        if num_agents == 0:
            num_agents = 1
        
        agent_spacing = min(0.4, 1.2 / num_agents)
        agent_y_start = agent_start_y - 0.1
        
        solution_ready = False
        
        for agent_idx, agent_name in enumerate(selected_agents):
            agent_y = agent_y_start - agent_idx * agent_spacing
            
            # Determine agent type and color
            agent_type = 'default'
            if 'planner' in agent_name.lower():
                agent_type = 'planner'
            elif 'decider' in agent_name.lower():
                agent_type = 'decider'
            elif 'critic' in agent_name.lower():
                agent_type = 'critic'
            elif 'cleaner' in agent_name.lower():
                agent_type = 'cleaner'
            elif 'conflict' in agent_name.lower():
                agent_type = 'conflict_resolver'
            elif 'expert' in agent_name.lower():
                agent_type = 'expert'
            
            color = color_map.get(agent_type, color_map['default'])
            
            # Check if solution ready
            for action in agent_actions:
                if action.get('agent') == agent_name:
                    result = action.get('result', {})
                    parsed = result.get('response', {})
                    if isinstance(parsed, dict) and parsed.get('is_solution_ready'):
                        solution_ready = True
                        color = '#FFD700'  # Gold for solution ready
            
            # Agent box
            agent_box = FancyBboxPatch((round_x + 0.05, agent_y - 0.12), round_width - 0.2, 0.12,
                                      boxstyle="round,pad=0.01",
                                      facecolor=color, edgecolor='black', linewidth=1.2, alpha=0.8)
            ax.add_patch(agent_box)
            
            # Agent name (shortened if too long)
            display_name = agent_name.replace('expert_', '').replace('_', ' ').title()
            if len(display_name) > 15:
                display_name = display_name[:12] + "..."
            
            ax.text(round_x + round_width/2, agent_y - 0.06, display_name,
                    ha='center', va='center', fontsize=8, weight='bold')
            
            # Store position for arrows
            y_positions[(round_idx, agent_name)] = agent_y - 0.12
        
        # Draw arrow from control unit
        arrow = FancyArrowPatch((round_x + round_width/2, control_y - 0.2),
                                (round_x + round_width/2, agent_start_y),
                                arrowstyle='->', mutation_scale=20, linewidth=1.5, color='black')
        ax.add_patch(arrow)
        
        # Solution ready indicator
        if solution_ready:
            solution_y = agent_y_start - num_agents * agent_spacing - 0.2
            solution_box = FancyBboxPatch((round_x, solution_y - 0.1), round_width - 0.1, 0.1,
                                          boxstyle="round,pad=0.01",
                                          facecolor='#FFD700', edgecolor='black', linewidth=2)
            ax.add_patch(solution_box)
            ax.text(round_x + round_width/2, solution_y - 0.05, "✓ SOLUTION READY",
                    ha='center', va='center', fontsize=9, weight='bold')
            current_y = solution_y - 0.3
        else:
            # Blackboard update
            blackboard_y = agent_y_start - num_agents * agent_spacing - 0.2
            snapshot = round_entry.get('blackboard_snapshot', {})
            public_count = len(snapshot.get('public_messages', []))
            ax.text(round_x + round_width/2, blackboard_y - 0.05,
                    f"Blackboard\n({public_count} msgs)",
                    ha='center', va='center', fontsize=7,
                    bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.5))
            current_y = blackboard_y - 0.3
        
        # Draw arrow to next round
        if round_idx < num_rounds - 1:
            next_round_x = start_x + (round_idx + 1) * round_width
            arrow = FancyArrowPatch((round_x + round_width, current_y + 0.2),
                                    (next_round_x, current_y + 0.2),
                                    arrowstyle='->', mutation_scale=20, linewidth=2, color='gray')
            ax.add_patch(arrow)
    
    # Legend
    legend_elements = [
        mpatches.Patch(facecolor=color_map['planner'], label='Planner'),
        mpatches.Patch(facecolor=color_map['decider'], label='Decider'),
        mpatches.Patch(facecolor=color_map['critic'], label='Critic'),
        mpatches.Patch(facecolor=color_map['expert'], label='Expert Agents'),
        mpatches.Patch(facecolor='#FFD700', label='Solution Ready'),
    ]
    ax.legend(handles=legend_elements, loc='lower center', bbox_to_anchor=(0.5, 0.02), ncol=5, fontsize=9)
    
    # Save figure
    plt.savefig(output_image, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    
    print(f"Image diagram saved to: {output_image}")
    return output_image


if __name__ == "__main__":
    import sys
    from typing import Optional
    
    if len(sys.argv) < 2:
        print("Usage: python visualize_trace.py <trace_json_file> [output_file] [--image output_image.png] [--paper-style] [--compare trace2.json]")
        print("\nOptions:")
        print("  output_file          - Save text visualization to file")
        print("  --image <file.png>   - Generate image diagram (PNG format)")
        print("  --paper-style        - Generate paper-style visualization (matches authors' illustration)")
        print("  --compare <file2>   - Compare two traces side-by-side (requires --paper-style)")
        sys.exit(1)
    
    trace_file = sys.argv[1]
    output_file = None
    output_image = None
    paper_style = False
    compare_file = None
    
    # Parse arguments
    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == '--image' and i + 1 < len(sys.argv):
            output_image = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--paper-style':
            paper_style = True
            i += 1
        elif sys.argv[i] == '--compare' and i + 1 < len(sys.argv):
            compare_file = sys.argv[i + 1]
            i += 2
        else:
            if output_file is None:
                output_file = sys.argv[i]
            i += 1
    
    # Generate text visualization
    visualize_flow(trace_file, output_file)
    create_ascii_diagram(trace_file)
    
    # Generate image if requested
    if paper_style:
        if compare_file:
            create_paper_style_diagram(trace_file, compare_file, output_image)
        else:
            create_paper_style_diagram(trace_file, None, output_image)
    elif output_image is not None:
        create_image_diagram(trace_file, output_image)

