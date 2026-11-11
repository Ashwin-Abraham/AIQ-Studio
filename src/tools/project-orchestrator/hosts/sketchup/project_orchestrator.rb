require 'json'
require 'sketchup.rb'

module AIQStudio
  module ProjectOrchestrator
    URL = 'http://127.0.0.1:5174/'.freeze

    def self.open
      if @dialog&.visible?
        @dialog.bring_to_front
        return
      end

      dialog = UI::HtmlDialog.new(
        dialog_title: 'AIQ Studio Project Orchestrator',
        preferences_key: 'AIQStudio.ProjectOrchestrator',
        width: 1100,
        height: 750,
        resizable: true
      )
      dialog.add_action_callback('selectProjectFolder') do |_context|
        result = choose_folder
        dialog.execute_script(
          "window.dispatchEvent(new CustomEvent('aiq-project-folder-selected', " \
          "{ detail: #{JSON.generate(result)} }));"
        )
      end
      dialog.set_url(URL)
      dialog.set_on_closed { @dialog = nil }
      @dialog = dialog
      dialog.show
    end

    def self.choose_folder
      path = UI.select_directory(title: 'Select project folder')
      return {} unless path

      subfolders = Dir.children(path).select do |name|
        File.directory?(File.join(path, name))
      end
      { folder: { name: File.basename(path), subfolders: subfolders } }
    rescue SystemCallError, IOError
      { error: true }
    end
  end
end

AIQStudio::ProjectOrchestrator.open
