const vscode = require('vscode');
const path = require('path');
const http = require('http');
const https = require('https');

function activate(context) {
    console.log('File Uploader extension activated');
    let disposable = vscode.commands.registerCommand('file-uploader.uploadFiles', async (uri) => {
        try {
            await uploadFiles(uri);
        } catch (error) {
            vscode.window.showErrorMessage(`Upload failed: ${error.message}`);
        }
    });
    context.subscriptions.push(disposable);
}

async function uploadFiles(uri) {
    if (!uri) {
        vscode.window.showErrorMessage('Please select a file or folder');
        return;
    }

    const files = [];
    const stat = await vscode.workspace.fs.stat(uri);
    
    if (stat.type === vscode.FileType.Directory) {
        const entries = await vscode.workspace.fs.readDirectory(uri);
        for (const [name, type] of entries) {
            if (type === vscode.FileType.File) {
                files.push(vscode.Uri.joinPath(uri, name));
            }
        }
    } else {
        files.push(uri);
    }

    if (files.length === 0) {
        vscode.window.showInformationMessage('No files to upload');
        return;
    }

    const config = vscode.workspace.getConfiguration('fileUploader');
    const serverUrl = config.get('serverUrl') || 'http://localhost:3000';

    await vscode.window.withProgress({
        location: vscode.ProgressLocation.Notification,
        title: `Uploading ${files.length} file(s)...`,
        cancellable: false
    }, async (progress) => {
        let successCount = 0;
        
        for (let i = 0; i < files.length; i++) {
            const file = files[i];
            const fileName = path.basename(file.fsPath);
            
            progress.report({ 
                message: `${fileName} (${i + 1}/${files.length})`,
                increment: (i / files.length) * 100
            });

            try {
                const content = await vscode.workspace.fs.readFile(file);
                const base64Content = Buffer.from(content).toString('base64');
                
                const postData = JSON.stringify({
                    filename: fileName,
                    content: base64Content,
                    path: file.fsPath
                });

                const url = new URL(serverUrl + '/upload');
                const lib = url.protocol === 'https:' ? https : http;
                
                await new Promise((resolve, reject) => {
                    const options = {
                        hostname: url.hostname,
                        port: url.port || (url.protocol === 'https:' ? 443 : 80),
                        path: url.pathname,
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'Content-Length': Buffer.byteLength(postData)
                        }
                    };

                    const req = lib.request(options, (res) => {
                        if (res.statusCode === 200) {
                            successCount++;
                            resolve();
                        } else {
                            reject(new Error(`HTTP ${res.statusCode}`));
                        }
                    });

                    req.on('error', reject);
                    req.write(postData);
                    req.end();
                });
                
            } catch (error) {
                console.error(`Failed to upload ${fileName}:`, error);
            }
        }

        if (successCount === files.length) {
            const openWebpage = await vscode.window.showInformationMessage(
                `Successfully uploaded ${successCount} file(s)!`,
                'Open Webpage'
            );
            if (openWebpage === 'Open Webpage') {
                vscode.env.openExternal(vscode.Uri.parse(serverUrl));
            }
        } else {
            vscode.window.showWarningMessage(`Uploaded ${successCount}/${files.length} files`);
        }
    });
}

function deactivate() {}
module.exports = {
    activate,
    deactivate
};