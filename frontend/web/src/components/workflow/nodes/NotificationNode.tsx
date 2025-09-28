import React from "react";
import { Handle, Position, NodeProps } from "reactflow";

const NotificationNode: React.FC<NodeProps> = ({ data }) => {
  return (
    <div className="workflow-node-content">
      <div className="workflow-node-label">{data.label}</div>
      <div className="workflow-node-config">
        {data.config?.notification_type &&
          `Type: ${data.config.notification_type}`}
      </div>
      <Handle
        type="target"
        position={Position.Top}
        id="input"
        style={{ background: "#faad14" }}
      />
      <Handle
        type="source"
        position={Position.Bottom}
        id="output"
        style={{ background: "#faad14" }}
      />
    </div>
  );
};

export default NotificationNode;
