const path = require("path");
const webpack = require("webpack");
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const CssMinimizerPlugin = require("css-minimizer-webpack-plugin");
const TerserPlugin = require("terser-webpack-plugin");
const CompressionPlugin = require("compression-webpack-plugin");
const { BundleAnalyzerPlugin } = require("webpack-bundle-analyzer");
const HtmlWebpackPlugin = require("html-webpack-plugin");
const CopyWebpackPlugin = require("copy-webpack-plugin");

module.exports = (env, argv) => {
  const isProduction = argv.mode === "production";
  const isDevelopment = !isProduction;

  return {
    mode: isProduction ? "production" : "development",
    entry: "./src/index.js",
    output: {
      path: path.resolve(__dirname, "build"),
      filename: isProduction ? "static/js/[name].[contenthash:8].js" : "[name].js",
      chunkFilename: isProduction ? "static/js/[name].[contenthash:8].chunk.js" : "[name].chunk.js",
      assetModuleFilename: isProduction ? "static/media/[name].[hash][ext]" : "[name].[ext]",
      clean: true,
      publicPath: "/",
      crossOriginLoading: "anonymous",
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
      },
    },
    module: {
      rules: [
        {
          test: /\.(ts|tsx)$/,
          use: [
            {
              loader: "ts-loader",
              options: {
                transpileOnly: isDevelopment,
                configFile: path.resolve(__dirname, "tsconfig.json"),
              },
            },
          ],
          exclude: /node_modules/,
        },
        {
          test: /\.(js|jsx)$/,
          use: [
            {
              loader: "babel-loader",
              options: {
                presets: [
                  ["@babel/preset-env", { targets: "defaults" }],
                  ["@babel/preset-react", { runtime: "automatic" }],
                  "@babel/preset-typescript",
                ],
                plugins: [
                  "@babel/plugin-proposal-class-properties",
                  "@babel/plugin-syntax-dynamic-import",
                  "@babel/plugin-transform-runtime",
                ],
              },
            },
          ],
          exclude: /node_modules/,
        },
        {
          test: /\.css$/,
          use: [
            isDevelopment ? "style-loader" : MiniCssExtractPlugin.loader,
            {
              loader: "css-loader",
              options: {
                importLoaders: 1,
                modules: {
                  auto: true,
                  localIdentName: isDevelopment ? "[name]__[local]--[hash:base64:5]" : "[hash:base64:8]",
                },
              },
            },
            {
              loader: "postcss-loader",
              options: {
                postcssOptions: {
                  plugins: [
                    ["autoprefixer"],
                    ...(isProduction ? [["cssnano", { preset: "default" }]] : []),
                  ],
                },
              },
            },
          ],
        },
        {
          test: /\.(png|jpe?g|gif|svg|webp)$/i,
          type: "asset/resource",
          generator: {
            filename: isProduction ? "static/images/[name].[hash][ext]" : "images/[name].[ext]",
          },
        },
        {
          test: /\.(woff|woff2|eot|ttf|otf)$/i,
          type: "asset/resource",
          generator: {
            filename: isProduction ? "static/fonts/[name].[hash][ext]" : "fonts/[name].[ext]",
          },
        },
      ],
    },
    plugins: [
      new webpack.DefinePlugin({
        "process.env.NODE_ENV": JSON.stringify(isProduction ? "production" : "development"),
        "process.env.REACT_APP_VERSION": JSON.stringify(process.env.npm_package_version || "1.0.0"),
        "process.env.REACT_APP_API_URL": JSON.stringify(process.env.REACT_APP_API_URL || "http://localhost:8000"),
        "process.env.REACT_APP_WS_URL": JSON.stringify(process.env.REACT_APP_WS_URL || "ws://localhost:8000/ws"),
      }),
      new HtmlWebpackPlugin({
        template: path.resolve(__dirname, "public/index.html"),
        filename: "index.html",
        inject: true,
        minify: isProduction ? {
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
        } : false,
      }),
      new MiniCssExtractPlugin({
        filename: isProduction ? "static/css/[name].[contenthash:8].css" : "[name].css",
        chunkFilename: isProduction ? "static/css/[name].[contenthash:8].chunk.css" : "[name].chunk.css",
      }),
      new CopyWebpackPlugin({
        patterns: [
          {
            from: path.resolve(__dirname, "public"),
            to: path.resolve(__dirname, "build"),
            globOptions: {
              ignore: ["**/index.html"],
            },
          },
        ],
      }),
      ...(isProduction ? [
        new CompressionPlugin({
          algorithm: "gzip",
          test: /\.(js|css|html|svg)$/,
          threshold: 8192,
          minRatio: 0.8,
        }),
        new webpack.optimize.ModuleConcatenationPlugin(),
        new webpack.IgnorePlugin({
          resourceRegExp: /^\.\/locale$/,
          contextRegExp: /moment$/,
        }),
      ] : []),
      ...(process.env.ANALYZE === "true" ? [
        new BundleAnalyzerPlugin({
          analyzerMode: "static",
          openAnalyzer: false,
          reportFilename: "bundle-report.html",
        }),
      ] : []),
    ],
    optimization: {
      minimize: isProduction,
      minimizer: [
        new TerserPlugin({
          terserOptions: {
            compress: {
              drop_console: isProduction,
              drop_debugger: isProduction,
              pure_funcs: isProduction ? ["console.log", "console.info"] : [],
            },
            format: {
              comments: false,
            },
          },
          extractComments: false,
        }),
        new CssMinimizerPlugin(),
      ],
      splitChunks: {
        chunks: "all",
        cacheGroups: {
          vendor: {
            test: /[\\/]node_modules[\\/]/,
            name: "vendors",
            chunks: "all",
            priority: 10,
          },
          common: {
            name: "common",
            minChunks: 2,
            chunks: "all",
            enforce: true,
            priority: 5,
          },
          react: {
            test: /[\\/]node_modules[\\/](react|react-dom)[\\/]/,
            name: "react",
            chunks: "all",
            priority: 20,
          },
          mui: {
            test: /[\\/]node_modules[\\/]@mui[\\/]/,
            name: "mui",
            chunks: "all",
            priority: 15,
          },
        },
      },
      runtimeChunk: {
        name: "runtime",
      },
    },
    devServer: {
      static: {
        directory: path.join(__dirname, "public"),
      },
      compress: true,
      port: 3000,
      hot: true,
      historyApiFallback: true,
      client: {
        overlay: {
          errors: true,
          warnings: false,
        },
      },
      proxy: {
        "/api": {
          target: "http://localhost:8000",
          changeOrigin: true,
          secure: false,
        },
        "/ws": {
          target: "ws://localhost:8000",
          ws: true,
          changeOrigin: true,
        },
      },
    },
    performance: {
      hints: isProduction ? "warning" : false,
      maxEntrypointSize: 512000,
      maxAssetSize: 512000,
    },
    stats: {
      chunks: true,
      chunkModules: true,
      chunkOrigins: true,
      modules: false,
      children: false,
      entrypoints: false,
    },
    devtool: isDevelopment ? "eval-source-map" : "source-map",
  };
};