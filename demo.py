#!/usr/bin/env python3
"""
Logistics Multi-Agent System Demo Script

Interactive demonstration of the agent orchestration system with predefined
example queries showcasing different agent capabilities and workflows.
"""

import sys
import os
from pathlib import Path

# Add Agents directory to path
sys.path.append(str(Path(__file__).parent / "Agents"))

from data_setup import initialize_dataframes
from agent_factory import initialize_agent_factory
from typing import Dict, Any

# Rich imports for beautiful terminal output
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown
from rich import box
from rich.prompt import Prompt
from rich.text import Text

console = Console()


class LogisticsDemo:
    """Interactive demo for the Logistics Multi-Agent System."""
    
    def __init__(self):
        """Initialize the demo system."""
        self.agents = {}
        self.factory = None
        self.streaming_enabled = True  # Default to streaming enabled
        self.current_model = "qwen2.5:3b"  # Default to fast model
        self.setup_system()
        
    def setup_system(self):
        """Set up the agent system."""
        console.print("\n[bold cyan]🚀 Initializing Logistics Multi-Agent System...[/]")
        try:
            # Initialize data
            inventory_df, agv_df, routes_df, approval_df = initialize_dataframes()
            
            # Create agent factory
            from data_providers.inventory_data_provider import InventoryDataProvider
            from data_providers.fleet_data_provider import FleetDataProvider
            from data_providers.approval_data_provider import ApprovalDataProvider
            
            inventory_manager = InventoryDataProvider(inventory_df)
            fleet_manager = FleetDataProvider(agv_df, routes_df)
            approval_manager = ApprovalDataProvider(approval_df)
            
            self.factory = initialize_agent_factory(
                inventory_manager, fleet_manager, approval_manager
            )
            
            # Create all agent types with A2A enabled for proper inter-agent communication
            agent_configs = [
                ("inventory", "DemoInventoryAgent"),
                ("fleet", "DemoFleetAgent"),
                ("approval", "DemoApprovalAgent"),
                ("orchestrator", "DemoOrchestratorAgent")
            ]
            
            for agent_type, name in agent_configs:
                agent = self.factory.create_agent(
                    agent_type=agent_type, 
                    name=name,
                    enable_a2a=True  # Enable A2A for proper multi-agent coordination
                )
                self.agents[agent_type] = agent
                console.print(f"[green]✅ Created {agent_type} agent: {name}[/]")
            
            console.print(f"\n[bold green]🎉 System initialized successfully with {len(self.agents)} agents![/]\n")
            
        except Exception as e:
            console.print(f"[bold red]❌ Error initializing system: {e}[/]")
            sys.exit(1)
    
    def display_banner(self):
        """Display the demo banner."""
        console.clear()
        
        banner_text = Text()
        banner_text.append("🏭 LOGISTICS MULTI-AGENT SYSTEM DEMO\n\n", style="bold cyan")
        banner_text.append("Experience the power of AI-driven logistics orchestration!\n", style="white")
        banner_text.append("Choose from example queries or create your own custom requests.\n", style="white")
        banner_text.append(f"⚡ Real-time streaming • 🚀 Model: {self.current_model}", style="yellow")
        
        console.print(Panel(banner_text, box=box.DOUBLE, border_style="cyan", padding=(1, 2)))
    
    def display_agent_status(self):
        """Display current agent status."""
        table = Table(title="📊 Agent Status", box=box.ROUNDED, border_style="blue")
        table.add_column("Type", style="cyan", no_wrap=True)
        table.add_column("Name", style="magenta")
        table.add_column("Tools", justify="right", style="green")
        table.add_column("Status", justify="center", style="yellow")
        
        for agent_type, agent in self.agents.items():
            if agent:
                info = agent.get_info()
                icon = {"inventory": "📦", "fleet": "🚛", "approval": "✅", "orchestrator": "🎯"}.get(agent_type, "🤖")
                table.add_row(
                    f"{icon} {agent_type.upper()}",
                    info['name'],
                    str(info['total_tools']),
                    "✓ Ready"
                )
            else:
                table.add_row(f"❌ {agent_type.upper()}", "Not available", "-", "✗ Error")
        
        console.print(table)
        console.print()
        
    def display_inventory_summary(self):
        """Display a summary of available inventory data."""
        table = Table(title="📦 Current Inventory Snapshot", box=box.ROUNDED, border_style="green")
        table.add_column("Part Number", style="cyan", no_wrap=True)
        table.add_column("Qty", justify="right", style="yellow")
        table.add_column("Cost/Unit", justify="right", style="green")
        table.add_column("Description", style="white")
        
        inventory_items = [
            ("HYDRAULIC-PUMP-HP450", "24", "$245.00", "Heavy-duty hydraulic pump"),
            ("PART-ABC123", "85", "$12.50", "Standard production part"), 
            ("PART-XYZ789", "42", "$18.75", "Specialized component"),
            ("PART-DEF456", "120", "$8.25", "Common component")
        ]
        
        for part_num, qty, cost, desc in inventory_items:
            table.add_row(part_num, qty, cost, desc)
        
        console.print(table)
        console.print("[dim]💡 These are real inventory items you can query in the demo![/]\n")
        
    def display_agv_summary(self):
        """Display a summary of available AGV fleet data."""
        table = Table(title="🚛 Current AGV Fleet Snapshot", box=box.ROUNDED, border_style="blue")
        table.add_column("AGV ID", style="cyan", no_wrap=True)
        table.add_column("Type", style="magenta")
        table.add_column("Capacity", justify="right", style="yellow")
        table.add_column("Status", style="green")
        table.add_column("Battery", justify="right", style="blue")
        table.add_column("Cost/km", justify="right", style="green")
        
        agv_fleet = [
            ("AGV-001", "Heavy Duty", "100 pcs", "AVAILABLE", "85%", "$5.00"),
            ("AGV-002", "Standard", "50 pcs", "AVAILABLE", "92%", "$3.50"),
            ("AGV-003", "Heavy Duty", "100 pcs", "AVAILABLE", "87%", "$5.00"),
            ("AGV-004", "Light Duty", "25 pcs", "AVAILABLE", "82%", "$2.50")
        ]
        
        for agv_id, agv_type, capacity, status, battery, cost in agv_fleet:
            table.add_row(agv_id, agv_type, capacity, status, battery, cost)
        
        console.print(table)
        console.print("[dim]💡 All AGVs currently at AGV_BASE and ready for deployment![/]\n")
        
    def display_approval_summary(self):
        """Display a summary of approval workflow data."""
        table = Table(title="✅ Current Approval Workflow Snapshot", box=box.ROUNDED, border_style="yellow")
        table.add_column("Level", style="cyan")
        table.add_column("Threshold", style="yellow")
        table.add_column("Requirement", style="magenta")
        table.add_column("", justify="center", style="green")
        
        approval_levels = [
            ("Low Value", "≤ $1,000", "Auto-Approved", "✅"),
            ("Medium Value", "$1,001 - $5,000", "Manager Required", "👨‍💼"),
            ("High Value", "> $5,000", "Director Required", "👔")
        ]
        
        for level, threshold, requirement, icon in approval_levels:
            table.add_row(level, threshold, requirement, icon)
        
        console.print(table)
        console.print("[dim]💡 Approval workflows automatically route based on order value![/]\n")
    
    def get_example_queries(self) -> Dict[str, Dict]:
        """Get predefined example queries organized by category."""
        return {
            "🏭 Inventory Management": {
                "1": {
                    "query": "Check current stock levels for all items in the warehouse",
                    "agent": "inventory",
                    "description": "Basic inventory overview"
                },
                "2": {
                    "query": "Find items with low stock levels that need replenishment",
                    "agent": "inventory", 
                    "description": "Low stock alert system"
                },
                "3": {
                    "query": "Get detailed information for HYDRAULIC-PUMP-HP450 including availability, cost, and supplier details",
                    "agent": "inventory",
                    "description": "Hydraulic pump lookup"
                },
                "4": {
                    "query": "Check inventory status for PART-ABC123 and PART-DEF456 - I need to know available quantities and warehouse locations",
                    "agent": "inventory", 
                    "description": "Multi-part inventory check"
                }
            },
            "🚛 Fleet Management": {
                "5": {
                    "query": "Show status of all AGVs and their current assignments",
                    "agent": "fleet",
                    "description": "Fleet status overview"
                },
                "6": {
                    "query": "Find the optimal route from Central Warehouse to Manufacturing Plant Delta for delivering hydraulic pumps",
                    "agent": "fleet",
                    "description": "Hydraulic equipment delivery route"
                },
                "7": {
                    "query": "Find and assign the best AGV to deliver 40 units from Warehouse A to Production Line A",
                    "agent": "fleet",
                    "description": "Urgent production parts delivery"
                }
            },
            "✅ Approval Workflows": {
                "8": {
                    "query": "Show all pending approval requests",
                    "agent": "approval",
                    "description": "Approval queue status"
                },
                "9": {
                    "query": "Create approval request for 20 units of HYDRAULIC-PUMP-HP450 ($4,900 total value) - this exceeds our standard approval threshold",
                    "agent": "approval",
                    "description": "High-value hydraulic equipment approval"
                },
                "10": {
                    "query": "Show me all approval requests and their current status",
                    "agent": "approval",
                    "description": "High-value approval audit trail"
                }
            },
            "🎯 Complex Orchestration": {
                "11": {
                    "query": "I need to deliver 15 units of HYDRAULIC-PUMP-HP450 to Manufacturing Plant Delta. Check inventory, get necessary approvals, find optimal AGV, and dispatch it.",
                    "agent": "orchestrator",
                    "description": "End-to-end hydraulic pump delivery"
                },
                "12": {
                    "query": "URGENT: Need to deliver 50 units of PART-ABC123 to Production Line A immediately. Get approvals and dispatch the fastest available AGV.",
                    "agent": "orchestrator", 
                    "description": "Emergency production parts delivery"
                },
                "13": {
                    "query": "Transfer 30 units of PART-XYZ789 to Production Line B. Handle approvals and coordinate AGV transport.",
                    "agent": "orchestrator",
                    "description": "Inter-warehouse parts transfer"
                }
            },
            "🔄 Cross-Agent Communication": {
                "14": {
                    "query": "Customer order: 25 units of PART-DEF456 to Manufacturing Plant Delta. Verify stock availability and assign appropriate AGV.",
                    "agent": "orchestrator",
                    "description": "Large order inventory-fleet coordination"
                },
                "15": {
                    "query": "High-value order: 20 units of HYDRAULIC-PUMP-HP450 to Production Line A. This is $4,900 total - need management approval before dispatch.",
                    "agent": "orchestrator",
                    "description": "High-value multi-agent workflow"
                },
                "16": {
                    "query": "What's our current logistics capacity? Show inventory levels, available AGVs, and any pending approvals. Suggest optimization opportunities.",
                    "agent": "orchestrator",
                    "description": "Complete system optimization"
                }
            }
        }
    
    def display_query_menu(self, examples: Dict):
        """Display the interactive query menu."""
        table = Table(title="📋 Example Queries", box=box.ROUNDED, border_style="magenta", show_header=False)
        table.add_column("Option", style="cyan bold", width=4)
        table.add_column("Description", style="white")
        
        for category, queries in examples.items():
            # Add category header
            table.add_row("", f"[bold yellow]{category}[/]")
            
            for num, details in queries.items():
                agent_icon = {
                    "inventory": "📦",
                    "fleet": "🚛", 
                    "approval": "✅",
                    "orchestrator": "🎯"
                }.get(details["agent"], "🤖")
                
                table.add_row(num, f"{agent_icon} {details['description']}")
        
        # Add control options
        table.add_row("", "")
        table.add_row("100", "💬 Custom query (enter your own)")
        table.add_row("200", f"⚡ Toggle streaming mode (currently: [bold]{'ON' if self.streaming_enabled else 'OFF'}[/])")
        table.add_row("300", f"🎮 Switch model (current: [bold]{self.current_model}[/])")
        table.add_row("400", "🚪 Quit demo")
        
        console.print(table)
    
    def execute_query(self, query: str, agent_type: str, streaming: bool = None) -> str:
        """Execute a query using the specified agent."""
        agent = self.agents.get(agent_type)
        if not agent:
            return f"❌ Error: {agent_type} agent not available"
        
        # Use instance setting if not specified
        if streaming is None:
            streaming = self.streaming_enabled
        
        try:
            response = agent.send_message(query, streaming=streaming)
            return response
        except Exception as e:
            return f"❌ Error executing query: {e}"
    
    def handle_custom_query(self):
        """Handle custom user query."""
        console.print("\n[bold cyan]💬 CUSTOM QUERY MODE[/]")
        
        # Show available agents in a table
        table = Table(box=box.SIMPLE, show_header=False)
        table.add_column("Option", style="cyan bold", width=4)
        table.add_column("Agent", style="white")
        
        agent_types = list(self.agents.keys())
        for i, agent_type in enumerate(agent_types, 1):
            icon = {"inventory": "📦", "fleet": "🚛", "approval": "✅", "orchestrator": "🎯"}.get(agent_type, "🤖")
            table.add_row(str(i), f"{icon} {agent_type}")
        
        console.print(table)
        
        try:
            agent_choice = input(f"\nSelect agent (1-{len(agent_types)}): ").strip()
            
            if agent_choice.isdigit() and 1 <= int(agent_choice) <= len(agent_types):
                selected_agent = agent_types[int(agent_choice) - 1]
                
                custom_query = input("Enter your query: ").strip()
                if custom_query:
                    response = self.execute_query(custom_query, selected_agent)
                    self.display_response(response)
                else:
                    console.print("[red]❌ Empty query entered.[/]")
            else:
                console.print("[red]❌ Invalid agent selection.[/]")
                
        except (KeyboardInterrupt, EOFError):
            console.print("\n[yellow]🚪 Returning to main menu...[/]")
    
    def handle_model_switch(self):
        """Handle model switching."""
        console.print("\n[bold cyan]🎮 MODEL SELECTION[/]")
        
        table = Table(box=box.SIMPLE, show_header=False)
        table.add_column("Option", style="cyan bold", width=4)
        table.add_column("Model", style="white")
        
        models = [
            ("1", "🚀 qwen2.5:3b", "Fast - Quick responses"),
            ("2", "🧠 qwen2.5:7b", "Powerful - Better reasoning"),
            ("3", "🦙 llama3.1:8b", "Alternative")
        ]
        
        for opt, name, desc in models:
            table.add_row(opt, f"{name} [dim]({desc})[/]")
        
        console.print(table)
        
        try:
            choice = input("\nSelect model (1-3): ").strip()
            
            model_map = {"1": "qwen2.5:3b", "2": "qwen2.5:7b", "3": "llama3.1:8b"}
            
            if choice not in model_map:
                console.print("[red]❌ Invalid selection.[/]")
                input("Press Enter to continue...")
                return
            
            new_model = model_map[choice]
            
            if new_model != self.current_model:
                console.print(f"\n[cyan]🔄 Switching from {self.current_model} to {new_model}...[/]")
                console.print("[yellow]⚠️ Note: Agents will be reinitialized with the new model.[/]")
                
                # Reinitialize with new model
                self.current_model = new_model
                self.factory._shared_model = None  # Reset shared model
                
                # Recreate agents with new model
                agent_configs = [
                    ("inventory", "DemoInventoryAgent"),
                    ("fleet", "DemoFleetAgent"),
                    ("approval", "DemoApprovalAgent"),
                    ("orchestrator", "DemoOrchestratorAgent")
                ]
                
                for agent_type, name in agent_configs:
                    agent = self.factory.create_agent(
                        agent_type=agent_type, 
                        name=name,
                        enable_a2a=True,
                        model_id=new_model
                    )
                    self.agents[agent_type] = agent
                
                console.print(f"[green]✅ Successfully switched to {new_model}![/]")
            else:
                console.print(f"[yellow]ℹ️ Already using {new_model}[/]")
            
            input("\nPress Enter to continue...")
            
        except (KeyboardInterrupt, EOFError):
            console.print("\n[yellow]🚪 Returning to main menu...[/]")
    
    def display_response(self, response: str):
        """Display agent response in a formatted way."""
        # Format the response in a nice panel
        console.print("\n")
        console.print(Panel(
            response,
            title="[bold green]🎯 Agent Response[/]",
            border_style="green",
            padding=(1, 2),
            box=box.ROUNDED
        ))
    
    def run_demo(self):
        """Run the interactive demo."""
        examples = self.get_example_queries()
        
        while True:
            try:
                self.display_banner()
                self.display_agent_status()
                self.display_inventory_summary()
                self.display_agv_summary()
                self.display_approval_summary()
                self.display_query_menu(examples)
                
                try:
                    choice = input("\n🎯 Select option: ").strip()
                except (EOFError, KeyboardInterrupt):
                    console.print("\n\n[bold yellow]👋 Demo interrupted. Goodbye![/]")
                    break
                
                if not choice:
                    # Empty input, just redraw menu
                    continue
                
                if choice == '400':
                    console.print("\n[bold green]👋 Thank you for trying the Logistics Multi-Agent System Demo![/]")
                    console.print("[cyan]🚀 Visit our documentation for more information and setup guides.[/]")
                    break
                
                elif choice == '100':
                    self.handle_custom_query()
                
                elif choice == '200':
                    self.streaming_enabled = not self.streaming_enabled
                    status = "[green]enabled[/]" if self.streaming_enabled else "[red]disabled[/]"
                    console.print(f"\n[bold]⚡ Streaming mode {status}![/]")
                    input("Press Enter to continue...")
                
                elif choice == '300':
                    self.handle_model_switch()
                    # Continue to next iteration to redraw menu
                    continue
                
                elif choice.isdigit():
                    # Find the query in examples
                    query_found = False
                    for category, queries in examples.items():
                        if choice in queries:
                            query_details = queries[choice]
                            response = self.execute_query(
                                query_details["query"], 
                                query_details["agent"]
                            )
                            self.display_response(response)
                            
                            try:
                                input("\nPress Enter to continue...")
                            except (EOFError, KeyboardInterrupt):
                                # Allow continuing even if Enter press is interrupted
                                pass
                            
                            query_found = True
                            break
                    
                    if not query_found:
                        console.print(f"[red]❌ Invalid selection: {choice}[/]")
                        try:
                            input("Press Enter to continue...")
                        except (EOFError, KeyboardInterrupt):
                            pass
                
                else:
                    console.print(f"[red]❌ Invalid option: {choice}[/]")
                    try:
                        input("Press Enter to continue...")
                    except (EOFError, KeyboardInterrupt):
                        pass
            
            except Exception as e:
                console.print(f"\n[bold red]❌ Unexpected error: {e}[/]")
                import traceback
                traceback.print_exc()
                try:
                    input("Press Enter to continue...")
                except (EOFError, KeyboardInterrupt):
                    break


def main():
    """Main demo function."""
    console.print("[bold cyan]🎬 Starting Logistics Multi-Agent System Demo...[/]")
    
    # Check prerequisites
    console.print("\n[cyan]🔍 Checking prerequisites...[/]")
    
    try:
        # Check if in correct directory
        if not Path("Agents").exists():
            console.print("[bold red]❌ Error: Please run this script from the project root directory.[/]")
            console.print("[yellow]   The 'Agents' directory should be in the current directory.[/]")
            sys.exit(1)
        
        # Check if Ollama is accessible (optional check)
        console.print("[green]✅ Directory structure looks good[/]")
        console.print("[dim]💡 Tip: Make sure Ollama is running with 'ollama serve' for best experience[/]\n")
        
        # Start demo
        demo = LogisticsDemo()
        demo.run_demo()
        
    except Exception as e:
        console.print(f"\n[bold red]❌ Error starting demo: {e}[/]")
        console.print("\n[bold yellow]🔧 Troubleshooting tips:[/]")
        console.print("[yellow]   1. Ensure you're in the project root directory[/]")
        console.print("[yellow]   2. Make sure all dependencies are installed: pip install -r requirements.txt[/]")
        console.print("[yellow]   3. Verify Ollama is running: ollama serve[/]")
        console.print("[yellow]   4. Check that the required model is available: ollama pull qwen2.5:7b[/]")


if __name__ == "__main__":
    main()