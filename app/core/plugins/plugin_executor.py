import importlib

def execute_plugin(plugin_name: str, input_text: str) -> dict:
    try:
        module_path = f"shared.plugins.{plugin_name}"
        plugin = importlib.import_module(module_path)

        if hasattr(plugin, "run"):
            output = plugin.run(input_text)
            return {
                "plugin": plugin_name,
                "input": input_text,
                "output": output
            }
        else:
            return { "error": f"Plugin '{plugin_name}' missing 'run()'" }

    except ModuleNotFoundError:
        return { "error": f"Plugin '{plugin_name}' not found." }
    except Exception as e:
        return { "error": str(e) }