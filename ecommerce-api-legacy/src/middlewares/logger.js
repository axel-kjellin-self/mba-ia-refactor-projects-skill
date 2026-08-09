/**
 * Request logging middleware
 * Logs all incoming requests with method, path, and response time
 */
function requestLogger(req, res, next) {
    const startTime = Date.now();

    // Log when response is finished
    res.on('finish', () => {
        const duration = Date.now() - startTime;
        const logMessage = `${req.method} ${req.path} ${res.statusCode} - ${duration}ms`;

        // Color code by status
        if (res.statusCode >= 500) {
            console.error(`[ERROR] ${logMessage}`);
        } else if (res.statusCode >= 400) {
            console.warn(`[WARN] ${logMessage}`);
        } else {
            console.log(`[INFO] ${logMessage}`);
        }
    });

    next();
}

module.exports = { requestLogger };
