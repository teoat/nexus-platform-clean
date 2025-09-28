const path = require("path");
const webpack = require("webpack");
const TerserPlugin = require("terser-webpack-plugin");
const CssMinimizerPlugin = require("css-minimizer-webpack-plugin");
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const CompressionPlugin = require("compression-webpack-plugin");
const { BundleAnalyzerPlugin } = require("webpack-bundle-analyzer");
const HtmlWebpackPlugin = require("html-webpack-plugin");
const CopyWebpackPlugin = require("copy-webpack-plugin");

module.exports = {
  mode: "production",
  entry: {
    main: "./src/index.js",
    vendor: [
      "react",
      "react-dom",
      "react-router-dom",
      "@mui/material",
      "@mui/icons-material",
      "@emotion/react",
      "@emotion/styled",
    ],
    charts: ["recharts"],
    utils: ["lodash-es", "date-fns"],
  },
  output: {
    path: path.resolve(__dirname, "build"),
    filename: "static/js/[name].[contenthash:8].js",
    chunkFilename: "static/js/[name].[contenthash:8].chunk.js",
    assetModuleFilename: "static/media/[name].[hash][ext]",
    clean: true,
    publicPath: "/",
    crossOriginLoading: "anonymous",
  },
  optimization: {
    minimize: true,
    minimizer: [
      new TerserPlugin({
        terserOptions: {
          parse: {
            ecma: 8,
          },
          compress: {
            ecma: 5,
            warnings: false,
            comparisons: false,
            inline: 2,
            drop_console: true,
            drop_debugger: true,
            pure_funcs: [
              "console.log",
              "console.info",
              "console.debug",
              "console.warn",
            ],
            passes: 2,
          },
          mangle: {
            safari10: true,
            properties: {
              regex: /^_/,
            },
          },
          output: {
            ecma: 5,
            comments: false,
            ascii_only: true,
          },
        },
        parallel: true,
        extractComments: false,
      }),
      new CssMinimizerPlugin({
        minimizerOptions: {
          preset: [
            "default",
            {
              discardComments: { removeAll: true },
              normalizeWhitespace: true,
              colormin: true,
              minifyFontValues: true,
              minifySelectors: true,
              mergeLonghand: true,
              mergeRules: true,
            },
          ],
        },
      }),
    ],
    splitChunks: {
      chunks: "all",
      minSize: 20000,
      maxSize: 244000,
      cacheGroups: {
        default: {
          minChunks: 2,
          priority: -20,
          reuseExistingChunk: true,
        },
        vendor: {
          test: /[\\/]node_modules[\\/]/,
          name: "vendors",
          priority: -10,
          chunks: "all",
          enforce: true,
        },
        mui: {
          test: /[\\/]node_modules[\\/]@mui[\\/]/,
          name: "mui",
          priority: 10,
          chunks: "all",
          enforce: true,
        },
        emotion: {
          test: /[\\/]node_modules[\\/]@emotion[\\/]/,
          name: "emotion",
          priority: 10,
          chunks: "all",
          enforce: true,
        },
        react: {
          test: /[\\/]node_modules[\\/](react|react-dom)[\\/]/,
          name: "react",
          priority: 20,
          chunks: "all",
          enforce: true,
        },
        charts: {
          test: /[\\/]node_modules[\\/](recharts|d3)[\\/]/,
          name: "charts",
          priority: 15,
          chunks: "all",
          enforce: true,
        },
        utils: {
          test: /[\\/]node_modules[\\/](lodash-es|date-fns)[\\/]/,
          name: "utils",
          priority: 15,
          chunks: "all",
          enforce: true,
        },
        common: {
          name: "common",
          minChunks: 2,
          priority: 5,
          chunks: "all",
          enforce: true,
        },
      },
    },
    runtimeChunk: {
      name: "runtime",
    },
    usedExports: true,
    sideEffects: false,
  },
  module: {
    rules: [
      {
        test: /\.(js|jsx|ts|tsx)$/,
        exclude: /node_modules/,
        use: {
          loader: "babel-loader",
          options: {
            presets: [
              [
                "@babel/preset-env",
                {
                  targets: { browsers: ["> 1%", "last 2 versions"] },
                  modules: false,
                  useBuiltIns: "usage",
                  corejs: 3,
                },
              ],
              ["@babel/preset-react", { runtime: "automatic" }],
              "@babel/preset-typescript",
            ],
            plugins: [
              "@babel/plugin-proposal-class-properties",
              "@babel/plugin-syntax-dynamic-import",
              ["@babel/plugin-transform-runtime", { useESModules: true }],
              ["@babel/plugin-transform-modules-commonjs", { strict: false }],
            ],
            cacheDirectory: true,
            cacheCompression: false,
          },
        },
      },
      {
        test: /\.css$/,
        use: [
          MiniCssExtractPlugin.loader,
          {
            loader: "css-loader",
            options: {
              modules: {
                auto: true,
                localIdentName: "[name]__[local]--[hash:base64:5]",
              },
              importLoaders: 1,
            },
          },
          {
            loader: "postcss-loader",
            options: {
              postcssOptions: {
                plugins: [
                  ["autoprefixer", { flexbox: "no-2009" }],
                  ["cssnano", { preset: "default" }],
                ],
              },
            },
          },
        ],
      },
      {
        test: /\.(png|jpe?g|gif|svg)$/i,
        type: "asset",
        parser: {
          dataUrlCondition: {
            maxSize: 8192, // 8kb
          },
        },
        generator: {
          filename: "static/images/[name].[hash][ext]",
        },
      },
      {
        test: /\.(woff|woff2|eot|ttf|otf)$/i,
        type: "asset/resource",
        generator: {
          filename: "static/fonts/[name].[hash][ext]",
        },
      },
    ],
  },
  resolve: {
    extensions: [".tsx", ".ts", ".jsx", ".js", ".json"],
    alias: {
      "@": path.resolve(__dirname, "src"),
      "@components": path.resolve(__dirname, "src/components"),
      "@pages": path.resolve(__dirname, "src/pages"),
      "@hooks": path.resolve(__dirname, "src/hooks"),
      "@services": path.resolve(__dirname, "src/services"),
      "@utils": path.resolve(__dirname, "src/utils"),
      "@types": path.resolve(__dirname, "src/types"),
      "@constants": path.resolve(__dirname, "src/constants"),
      "@store": path.resolve(__dirname, "src/store"),
      "@contexts": path.resolve(__dirname, "src/contexts"),
    },
    fallback: {
      crypto: false,
      stream: false,
      util: false,
    },
  },
  plugins: [
    new webpack.DefinePlugin({
      "process.env.NODE_ENV": JSON.stringify("production"),
      "process.env.REACT_APP_VERSION": JSON.stringify(
        process.env.npm_package_version,
      ),
      "process.env.REACT_APP_BUILD_TIME": JSON.stringify(
        new Date().toISOString(),
      ),
    }),
    new HtmlWebpackPlugin({
      template: "./public/index.html",
      minify: {
        removeComments: true,
        collapseWhitespace: true,
        removeRedundantAttributes: true,
        useShortDoctype: true,
        removeEmptyAttributes: true,
        removeStyleLinkTypeAttributes: true,
        keepClosingSlash: true,
        minifyJS: true,
        minifyCSS: true,
        minifyURLs: true,
      },
    }),
    new MiniCssExtractPlugin({
      filename: "static/css/[name].[contenthash:8].css",
      chunkFilename: "static/css/[name].[contenthash:8].chunk.css",
    }),
    new CompressionPlugin({
      algorithm: "gzip",
      test: /\.(js|css|html|svg)$/,
      threshold: 8192,
      minRatio: 0.8,
    }),
    new CopyWebpackPlugin({
      patterns: [
        {
          from: "public",
          to: ".",
          globOptions: {
            ignore: ["**/index.html"],
          },
        },
      ],
    }),
    new webpack.optimize.ModuleConcatenationPlugin(),
    new webpack.IgnorePlugin({
      resourceRegExp: /^\.\/locale$/,
      contextRegExp: /moment$/,
    }),
    new webpack.ProvidePlugin({
      React: "react",
    }),
    ...(process.env.ANALYZE === "true"
      ? [
          new BundleAnalyzerPlugin({
            analyzerMode: "static",
            openAnalyzer: false,
            reportFilename: "bundle-report.html",
            generateStatsFile: true,
            statsFilename: "bundle-stats.json",
          }),
        ]
      : []),
  ],
  performance: {
    hints: "warning",
    maxEntrypointSize: 512000,
    maxAssetSize: 512000,
    assetFilter: (assetFilename) => {
      return !assetFilename.endsWith(".map");
    },
  },
  stats: {
    chunks: true,
    chunkModules: true,
    chunkOrigins: true,
    modules: false,
    children: false,
    entrypoints: false,
    assets: true,
    timings: true,
    builtAt: true,
    version: true,
  },
  experiments: {
    topLevelAwait: true,
  },
};
