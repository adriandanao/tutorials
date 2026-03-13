/** @odoo-module **/

import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { Component, useState, useRef, onWillUnmount } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

class WebcamWidget extends Component {
  static template = "attendance_tracking.WebcamWidget";
  static props = { ...standardFieldProps };

  setup() {
    this.orm = useService("orm");
    this.state = useState({ streaming: false });
    this.videoRef = useRef("video");
    this.canvasRef = useRef("canvas");
    this._stream = null;

    onWillUnmount(() => this._stopStream());
  }

  async startCamera() {
    try {
      this._stream = await navigator.mediaDevices.getUserMedia({ video: true });
      const video = this.videoRef.el;
      video.srcObject = this._stream;
      await video.play();
      this.state.streaming = true;
    } catch (e) {
      console.error("Error accessing webcam:", e);
    }
  }

  async capture() {
    const video = this.videoRef.el;
    const canvas = this.canvasRef.el;
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext("2d").drawImage(video, 0, 0);
    const dataUrl = canvas.toDataURL("image/jpeg");
    // Strip prefix before saving
    const base64 = dataUrl.replace(/^data:image\/\w+;base64,/, "");
    this.props.record.update({ [this.props.name]: base64 });
    await this.props.record.save();
    this._stopStream();
  }

  async retake() {
    await this.orm.write(
      this.props.record.resModel,
      [this.props.record.resId],
      { [this.props.name]: false },
    );
    await this.props.record.load();
    this.startCamera();
  }

  _stopStream() {
    if (this._stream) {
      this._stream.getTracks().forEach((t) => t.stop());
      this._stream = null;
      this.state.streaming = false;
    }
  }
}

// ✅ Must be wrapped in an object with 'component' key
registry.category("fields").add("webcam", {
  component: WebcamWidget,
  supportedTypes: ["binary"], // ✅ belongs here, not on the class
});
