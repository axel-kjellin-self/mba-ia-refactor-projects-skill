const express = require('express');

const buildContainer = require('./container');
const buildRouter = require('./routes');
const requestLogger = require('./middlewares/requestLogger');
const { notFoundHandler, errorHandler } = require('./middlewares/errorHandler');

/**
 * Application factory: monta a instância Express a partir de um container de
 * dependências já resolvido. Não inicia o servidor nem abre conexões — isso
 * fica em `server.js`, o que torna a app instanciável em testes.
 *
 * @param {{db: import('./config/database')}} deps
 */
function createApp({ db, paymentGateway } = {}) {
    const app = express();
    const container = buildContainer({ db, paymentGateway });

    app.use(express.json({ limit: '100kb' }));
    app.use(requestLogger);

    app.use('/api', buildRouter(container));

    // Ordem importa: 404 e error handler sempre por último.
    app.use(notFoundHandler);
    app.use(errorHandler);

    return app;
}

module.exports = createApp;
