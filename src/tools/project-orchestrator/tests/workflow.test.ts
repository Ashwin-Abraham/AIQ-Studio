// @vitest-environment jsdom
import { describe, expect, it } from "vitest";
import { mount } from "@vue/test-utils";
import ProjectOrchestrator from "../src/ProjectOrchestrator.vue";
import WorkflowNode from "../src/components/WorkflowNode.vue";
import { loadProject, projectFileUrl } from "../src/WorkflowService";
import { fitView, zoomView } from "../src/ViewportService";

describe("project workflow", () => {
  it("selects a stage with the keyboard and shows its record and files", async () => {
    const wrapper = mount(ProjectOrchestrator, {
      props: {
        project: {
          name: "Test project",
          workflow: {
            nodes: {
              "site-data": {
                status: "complete",
                summary: "Survey checked.",
                decisions: ["Use the survey."],
                files: [{ path: "source/site data.md", label: "Survey" }],
              },
            },
          },
        },
      },
    });
    expect(wrapper.find("h1").text()).toBe("Test project");
    expect(wrapper.findAllComponents(WorkflowNode)).toHaveLength(9);
    await wrapper
      .get('[aria-label="Site data, Complete"]')
      .trigger("keydown", { key: "Enter" });
    expect(wrapper.find("aside").text()).toContain("Survey checked.");
    expect(wrapper.find("aside").text()).toContain("Use the survey.");
    expect(wrapper.find("aside a").attributes("href")).toBe(
      "./source/site%20data.md",
    );
    await wrapper
      .get('[aria-label="Project goals, Not started"]')
      .trigger("click");
    expect(wrapper.find("aside").text()).toContain("No summary recorded.");
    expect(wrapper.find("aside").text()).toContain("No decisions recorded.");
    expect(wrapper.find("aside").text()).toContain("No files recorded.");
    wrapper.unmount();
  });

  it("zooms and restores the full diagram with Fit", async () => {
    const wrapper = mount(ProjectOrchestrator, { props: { project: {} } });
    await wrapper.get('[aria-label="Zoom in"]').trigger("click");
    expect(wrapper.get("output").text()).toBe("120%");
    const fit = wrapper
      .findAll("button")
      .find((button) => button.text() === "Fit")!;
    await fit.trigger("click");
    expect(wrapper.get("svg").attributes("viewBox")).toBe("0 0 1250 286");
    wrapper.unmount();
  });

  it("loads an embedded project record for a standalone export", () => {
    const script = document.createElement("script");
    script.id = "project-data";
    script.type = "application/json";
    script.textContent = JSON.stringify({ name: "Exported project" });
    document.body.append(script);
    expect(loadProject()).toEqual({
      project: { name: "Exported project" },
      fileBase: "./",
    });
    script.remove();
  });

  it("keeps file links inside the project", () => {
    for (const path of [
      "../private",
      "/absolute",
      "https://example.com",
      "a\\b",
      "a/../../b",
      "a?b",
    ]) {
      expect(projectFileUrl(path, "./")).toBeUndefined();
    }
    expect(projectFileUrl("reports/café notes.md", "./")).toBe(
      "./reports/caf%C3%A9%20notes.md",
    );
  });

  it("keeps the zoom anchor fixed and applies the zoom limits", () => {
    const view = zoomView(fitView(), 2, 100, 50);
    expect((100 - view.x) / view.width).toBeCloseTo(100 / 1250);
    expect((50 - view.y) / view.height).toBeCloseTo(50 / 286);
    expect(zoomView(fitView(), 100, 0, 0).width).toBe(1250 / 4);
    expect(zoomView(fitView(), 0.001, 0, 0).width).toBe(1250 / 0.35);
  });
});
