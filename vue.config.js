const path = require('path');
let HtmlWebpackPlugin = require('html-webpack-plugin');
let HtmlWebpackInlineSourcePlugin = require('html-webpack-inline-source-plugin');

module.exports = {
  publicPath: '',
  outputDir: path.resolve(__dirname, 'cloudsplaining', 'output', 'dist'),
  filenameHashing: false,
  pages: {
    index: {
      // entry for the page
      entry: 'cloudsplaining/output/src/main.js',
      // the source template
      template: 'cloudsplaining/output/public/index.html',
      // output as dist/index.html
      filename: 'index.html',
      // filename: 'cloudsplaining/output/dist/index.html',
      // when using title option,
      // template title tag needs to be <title><%= htmlWebpackPlugin.options.title %></title>
      // title: '',
      // chunks to include on this page, by default includes
      // extracted common chunks and vendor chunks.
      chunks: ['chunk-vendors']
    },
  },
  configureWebpack: {
    output: {
      filename: '[name].bundle.js',
      // path: path.resolve(__dirname, 'dist'),
    },
    plugins: [
      new HtmlWebpackInlineSourcePlugin(),
      new HtmlWebpackPlugin({
        inlineSource: '.(js|css)$', // embed all javascript and css inline
        inject: true,
        template: 'cloudsplaining/output/public/index.html',  //template file to embed the source
        title: 'Cloudsplaining report',
      }),
    ],
    optimization: {
      splitChunks: {
        name: false,
        chunks: 'async',
        hidePathInfo: true,
      }
    },
    module: {
      rules: [
        {
          test: /\.md$/,
          use: [
            // {
            //   loader: "raw-loader",
            // },
            {
              loader: "html-loader"
            },
            {
              loader: "markdown-loader",
            },
          ]
        },
      ]
    }
  },
  css: {extract: false}
}
