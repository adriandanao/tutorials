/** @odoo-module **/
import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { Component } from "@odoo/owl";

export class VideoWidget extends Component {
  static template = "attendance_tracking.VideoWidget";
  static props = { ...standardFieldProps };

  get videoUrl() {
    return this.props.record.data[this.props.name] || "";
  }

  get embedUrl() {
    const url = this.videoUrl;
    if (!url) return "";

    // Convert YouTube watch URL to embed URL
    const match = url.match(/(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&\s]+)/);
    if (match) {
      return `https://www.youtube.com/embed/${match[1]}`;
    }

    // Return as-is for direct video files
    return url;
  }

  get isYoutube() {
    return (
      this.videoUrl.includes("youtube.com") ||
      this.videoUrl.includes("youtu.be")
    );
  }

  onUrlChange(ev) {
    this.props.record.update({ [this.props.name]: ev.target.value });
  }
}

registry.category("fields").add("videoWidget", {
  component: VideoWidget,
  supportedTypes: ["char"],
});
