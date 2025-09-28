import React from "react";
import { Handle, Position, NodeProps } from "reactflow";

const TransformNode: React.FC<NodeProps> = ({ data }) => {
  return (
    <div className="workflow-node-content">
      <div className="workflow-node-label">{data.label}</div>
      <div className="workflow-node-config">
        {data.config?.transform_type && `Type: ${data.config.transform_type}`}
      </div>
      <Handle
        type="target"
        position={Position.Top}
        id="input"
        style={{ background: "#fa8c16" }}
      />
      <Handle
        type="source"
        position={Position.Bottom}
        id="output"
        style={{ background: "#fa8c16" }}
      />
    </div>
  );
};

export default TransformNode;
