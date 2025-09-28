module.exports = {
  presets: [
    [
      "@babel/preset-env",
      {
        targets: {
          browsers: ["> 1%", "last 2 versions", "not dead"],
        },
        modules: false,
        useBuiltIns: "usage",
        corejs: 3,
      },
    ],
    [
      "@babel/preset-react",
      {
        runtime: "automatic",
      },
    ],
    "@babel/preset-typescript",
  ],
  plugins: [
    "@babel/plugin-proposal-class-properties",
    "@babel/plugin-syntax-dynamic-import",
    [
      "@babel/plugin-transform-runtime",
      {
        useESModules: true,
      },
    ],
  ],
  env: {
    development: {
      plugins: ["react-refresh/babel"],
    },
    production: {
      plugins: [
        [
          "transform-remove-console",
          {
            exclude: ["error", "warn"],
          },
        ],
      ],
    },
  },
};
