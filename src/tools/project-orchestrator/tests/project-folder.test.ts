// @vitest-environment jsdom
import { flushPromises, mount } from "@vue/test-utils";
import { afterEach, describe, expect, it, vi } from "vitest";
import ProjectFilesPanel from "../src/components/ProjectFilesPanel.vue";

afterEach(() => vi.unstubAllGlobals());

describe("project folder selection", () => {
  it("shows the initial project subfolders when the browser has no picker", () => {
    vi.stubGlobal("showDirectoryPicker", undefined);
    vi.stubGlobal("sketchup", undefined);
    const panel = mount(ProjectFilesPanel, {
      props: {
        initialFolder: {
          name: "site-planning-project",
          subfolders: ["01_Admin", "03_Site_Research"],
        },
      },
    });
    expect(panel.get("h3").text()).toBe("site-planning-project");
    expect(panel.findAll("li").map((item) => item.text())).toEqual([
      "01_Admin",
      "03_Site_Research",
    ]);
    panel.unmount();
  });

  it("lists only immediate directories and keeps the selection after cancellation", async () => {
    const picker = vi
      .fn()
      .mockResolvedValueOnce({
        name: "Example project",
        async *values() {
          yield { kind: "directory", name: "03 Research" };
          yield { kind: "file", name: "project.json" };
          yield { kind: "directory", name: "01 Empty" };
        },
      })
      .mockRejectedValueOnce(new DOMException("Cancelled", "AbortError"));
    vi.stubGlobal("showDirectoryPicker", picker);
    const panel = mount(ProjectFilesPanel);

    await panel.get("button").trigger("click");
    await flushPromises();
    expect(picker).toHaveBeenCalledWith({ mode: "read" });
    expect(panel.get("h3").text()).toBe("Example project");
    expect(panel.findAll("li").map((item) => item.text())).toEqual([
      "01 Empty",
      "03 Research",
    ]);

    await panel.get("button").trigger("click");
    await flushPromises();
    expect(panel.get("h3").text()).toBe("Example project");
    expect(panel.text()).not.toContain("Could not read");
    panel.unmount();
  });

  it("shows an empty folder returned by SketchUp, then reports a read failure", async () => {
    function sendResult(detail: object) {
      window.dispatchEvent(
        new CustomEvent("aiq-project-folder-selected", { detail }),
      );
    }
    const picker = vi
      .fn()
      .mockImplementationOnce(() =>
        sendResult({ folder: { name: "Empty", subfolders: [] } }),
      )
      .mockImplementationOnce(() => sendResult({ error: true }));
    vi.stubGlobal("sketchup", { selectProjectFolder: picker });
    const panel = mount(ProjectFilesPanel);

    await panel.get("button").trigger("click");
    await flushPromises();
    expect(panel.text()).toContain("This folder has no subfolders.");
    await panel.get("button").trigger("click");
    await flushPromises();
    expect(panel.text()).toContain("Could not read that folder.");
    expect(panel.get("button").text()).toBe("Change folder");
    panel.unmount();
  });
});
