import React from "react";
import { Handle, Position, NodeProps } from "reactflow";

const DataInputNode: React.FC<NodeProps> = ({ data }) => {
  return (
    <div className="workflow-node-content">
      <div className="workflow-node-label">{data.label}</div>
      <div className="workflow-node-config">
        {data.config?.input_key && `Key: ${data.config.input_key}`}
      </div>
      <Handle
        type="source"
        position={Position.Bottom}
        id="output"
        style={{ background: "#1890ff" }}
      />
    </div>
  );
};

export default DataInputNode;
