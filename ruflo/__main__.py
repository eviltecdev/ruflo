"""Ruflo CLI entry point."""

import sys
import argparse
import asyncio
import json
from typing import Optional

from ruflo.http_client import create_client
from ruflo.utils.logging import Logger

logger = Logger.get_logger(__name__)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Ruflo — Unified AI Agent Monolith",
        prog="python3 -m ruflo"
    )

    # Global options
    parser.add_argument(
        "--runtime-url",
        default="http://localhost:5000",
        help="Runtime server URL (default: http://localhost:5000)"
    )
    parser.add_argument(
        "--control-url",
        default="http://localhost:5000",
        help="Control server URL (default: http://localhost:5000)"
    )
    parser.add_argument(
        "--token",
        help="API token for authenticated endpoints"
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Server command
    server_parser = subparsers.add_parser("server", help="Start Ruflo servers")
    server_parser.add_argument(
        "--mode",
        choices=["combined", "local", "dashboard"],
        default="combined",
        help="Server mode: combined, local, or dashboard"
    )
    server_parser.add_argument(
        "--port",
        type=int,
        default=5000,
        help="Port for server (default: 5000)"
    )
    server_parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host to bind to (default: 127.0.0.1)"
    )

    # Health commands
    subparsers.add_parser("health", help="Check server health")
    subparsers.add_parser("ready", help="Check server readiness")
    subparsers.add_parser("status", help="Get system status")

    # Execution commands
    execute_parser = subparsers.add_parser("execute", help="Execute shell command")
    execute_parser.add_argument("command", help="Command to execute")

    task_parser = subparsers.add_parser("task", help="Execute structured task")
    task_parser.add_argument("task", help="Task name")
    task_parser.add_argument("--input", help="Task input (JSON)")

    # Control commands
    skills_parser = subparsers.add_parser("skills", help="List skills")
    skills_parser.add_argument("--limit", type=int, default=10, help="Limit results")

    subparsers.add_parser("workflows", help="List workflows")

    route_parser = subparsers.add_parser("route-task", help="Route task to skill")
    route_parser.add_argument("description", help="Task description")

    subparsers.add_parser("costs", help="Get cost tracking")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    # Create HTTP client
    client = create_client(
        runtime_url=args.runtime_url,
        control_url=args.control_url,
        api_token=args.token
    )

    try:
        if args.command == "server":
            return _start_servers(args)
        elif args.command == "health":
            return _health(client)
        elif args.command == "ready":
            return _ready(client)
        elif args.command == "status":
            return _status(client)
        elif args.command == "execute":
            return _execute(client, args.command)
        elif args.command == "task":
            return _task(client, args.task, args.input)
        elif args.command == "skills":
            return _skills(client, args.limit)
        elif args.command == "workflows":
            return _workflows(client)
        elif args.command == "route-task":
            return _route_task(client, args.description)
        elif args.command == "costs":
            return _costs(client)
        else:
            parser.print_help()
            return 1
    except Exception as e:
        logger.error(f"Command failed: {e}")
        return 1


def _start_servers(args):
    """Start Ruflo servers."""
    from ruflo.local_server.main import create_local_server
    from ruflo.dashboard_server import create_dashboard_server

    print(f"Starting Ruflo servers (mode: {args.mode}) on {args.host}:{args.port}...")

    if args.mode == "combined":
        # Create both servers and run on same port
        app = create_local_server()
        try:
            app.run(host=args.host, port=args.port, debug=False)
        except KeyboardInterrupt:
            print("\nShutdown gracefully...")
            return 0
    elif args.mode == "local":
        app = create_local_server()
        try:
            app.run(host=args.host, port=args.port, debug=False)
        except KeyboardInterrupt:
            print("\nShutdown gracefully...")
            return 0
    elif args.mode == "dashboard":
        app = create_dashboard_server()
        try:
            app.run(host=args.host, port=args.port, debug=False)
        except KeyboardInterrupt:
            print("\nShutdown gracefully...")
            return 0

    return 0


def _health(client) -> int:
    """Check health."""
    try:
        result = client.runtime().health()
        print(json.dumps(result, indent=2))
        return 0
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return 1


def _ready(client) -> int:
    """Check readiness."""
    try:
        result = client.runtime().ready()
        ready = result.get("ready", False)
        print(json.dumps(result, indent=2))
        return 0 if ready else 1
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return 1


def _status(client) -> int:
    """Get status."""
    try:
        result = client.runtime().status()
        print(json.dumps(result, indent=2))
        return 0
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        return 1


def _execute(client, command: str) -> int:
    """Execute shell command."""
    try:
        result = client.runtime().execute(command)
        if isinstance(result, dict):
            print(json.dumps(result, indent=2))
        else:
            print(result)
        return 0
    except Exception as e:
        logger.error(f"Execution failed: {e}")
        return 1


def _task(client, task: str, input_json: Optional[str]) -> int:
    """Execute structured task."""
    try:
        task_input = {}
        if input_json:
            task_input = json.loads(input_json)

        result = client.runtime().task(task, task_input)
        print(json.dumps(result, indent=2))
        return 0
    except Exception as e:
        logger.error(f"Task execution failed: {e}")
        return 1


def _skills(client, limit: int) -> int:
    """List skills."""
    try:
        result = client.control().list_skills(limit=limit)
        print(json.dumps(result, indent=2))
        return 0
    except Exception as e:
        logger.error(f"Skills listing failed: {e}")
        return 1


def _workflows(client) -> int:
    """List workflows."""
    try:
        result = client.control().list_workflows()
        print(json.dumps(result, indent=2))
        return 0
    except Exception as e:
        logger.error(f"Workflows listing failed: {e}")
        return 1


def _route_task(client, description: str) -> int:
    """Route task."""
    try:
        result = client.control().route_task(description)
        print(json.dumps(result, indent=2))
        return 0
    except Exception as e:
        logger.error(f"Task routing failed: {e}")
        return 1


def _costs(client) -> int:
    """Get costs."""
    try:
        result = client.control().costs()
        print(json.dumps(result, indent=2))
        return 0
    except Exception as e:
        logger.error(f"Cost retrieval failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
