import React from "react";
import { Handle, Position, NodeProps } from "reactflow";

const StartNode: React.FC<NodeProps> = ({ data }) => {
  return (
    <div className="workflow-node-content">
      <div className="workflow-node-label">{data.label}</div>
      <Handle
        type="source"
        position={Position.Bottom}
        id="output"
        style={{ background: "#52c41a" }}
      />
    </div>
  );
};

export default StartNode;
