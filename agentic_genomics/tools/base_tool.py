from adk.tools import Tool, ToolDeclaration

class BaseTool(Tool):
    def _get_declaration(self) -> ToolDeclaration:
        return ToolDeclaration(
            name=self.__class__.__name__,
            description=f"Placeholder for {self.__class__.__name__}.",
            parameters=[], # No parameters for placeholder
            # outputs={} # No specific outputs for placeholder
        )

    def run(self, **kwargs) -> dict:
        print(f"{self.__class__.__name__} executed (placeholder).")
        return {"status": "executed_placeholder"}
