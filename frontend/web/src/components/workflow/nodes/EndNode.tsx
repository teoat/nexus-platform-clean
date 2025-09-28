import React from "react";
import { Handle, Position, NodeProps } from "reactflow";

const EndNode: React.FC<NodeProps> = ({ data }) => {
  return (
    <div className="workflow-node-content">
      <div className="workflow-node-label">{data.label}</div>
      <Handle
        type="target"
        position={Position.Top}
        id="input"
        style={{ background: "#ff4d4f" }}
      />
    </div>
  );
};

export default EndNode;
