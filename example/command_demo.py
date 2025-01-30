from grpy.tools.command_manager import CommandManager


def main():
    # Define commands to execute
    commands = [
        ["ls", "-la"],
    ]

    # Initialize CommandManager with commands
    cm = CommandManager(cmds=commands, cmd_whitelist=["ls"])

    # Execute all commands in sequence
    cm.run_commands()


if __name__ == "__main__":
    main()
