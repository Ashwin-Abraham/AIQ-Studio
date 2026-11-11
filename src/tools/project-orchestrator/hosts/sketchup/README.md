# SketchUp launcher

This developer script opens the local Project Orchestrator app in a SketchUp dialog.

1. [Start the local server](../../README.md) and keep it running.
2. In SketchUp's Ruby Console, run the command below. Replace `TOOL_PATH` with the full path to the Project Orchestrator folder. Use forward slashes.

   ```ruby
   load 'TOOL_PATH/hosts/sketchup/project_orchestrator.rb'
   ```

3. Click **Select folder**. SketchUp opens its folder picker. **Project files** shows the selected folder and its immediate subfolders.

The planned entry point for regular use is a command in the SketchUp Extensions menu.
