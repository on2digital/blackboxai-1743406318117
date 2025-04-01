module.exports = function override(config, env) {
  config.devServer = {
    ...config.devServer,
    allowedHosts: 'all',
    host: '0.0.0.0',
    port: 3001,
    disableHostCheck: true
  };
  return config;
}