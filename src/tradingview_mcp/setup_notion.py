"""
Notion Setup Utility
====================
Interactive script to set up Notion database for TradingView sync.
"""

import logging
import os
from pathlib import Path

from dotenv import load_dotenv

from tradingview_mcp.notion_sync import NotionSync

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("notion-setup")

load_dotenv()


def setup_notion() -> None:
    """Interactive setup for Notion database."""
    print("\n=== TradingView Notion Sync Setup ===\n")

    # Get Notion token
    notion_token = os.getenv("NOTION_TOKEN")
    if not notion_token:
        notion_token = input("Enter your Notion API token: ").strip()
        if not notion_token:
            print("Error: Notion token is required.")
            return

    # Initialize Notion client
    try:
        sync = NotionSync(notion_token)
        print("✓ Notion connection successful!")
    except Exception as e:
        print(f"✗ Failed to connect to Notion: {e}")
        return

    # Get parent page ID
    parent_page_id = input("\nEnter the Notion Page ID where you want to create the database\n(You can get this from the URL of your Notion page): ").strip()
    if not parent_page_id:
        print("Error: Parent page ID is required.")
        return

    # Validate parent page ID format
    if len(parent_page_id) != 36:  # Notion IDs are typically 36 chars with hyphens
        print("Warning: Page ID might be invalid (should be 36 characters)")

    # Create database
    try:
        print("\nCreating Notion database...")
        database_id = sync.create_database(parent_page_id, "TradingView Analysis")
        print(f"✓ Database created successfully!")
        print(f"Database ID: {database_id}\n")

        # Save to .env file
        save_to_env = input("Would you like to save the configuration to .env file? (y/n): ").strip().lower()
        if save_to_env == "y":
            env_file = Path(".env")
            env_content = f"NOTION_TOKEN={notion_token}\nNOTION_DATABASE_ID={database_id}\n"

            if env_file.exists():
                with open(env_file, "a") as f:
                    f.write(env_content)
                print("✓ Configuration appended to .env file")
            else:
                with open(env_file, "w") as f:
                    f.write(env_content)
                print("✓ .env file created with configuration")

            # Add .env to .gitignore
            gitignore_path = Path(".gitignore")
            if gitignore_path.exists():
                with open(gitignore_path, "r") as f:
                    gitignore_content = f.read()
                if ".env" not in gitignore_content:
                    with open(gitignore_path, "a") as f:
                        f.write("\n.env\n")
            else:
                with open(gitignore_path, "w") as f:
                    f.write(".env\n")

        print("\n=== Setup Complete ===")
        print("Next steps:")
        print("1. Run: uv sync")
        print("2. Run: uv run tradingview-daily-sync")
        print("   (Or set up a daily cron job)")

    except Exception as e:
        print(f"✗ Failed to create database: {e}")


def main():
    """CLI entry point."""
    setup_notion()


if __name__ == "__main__":
    main()
