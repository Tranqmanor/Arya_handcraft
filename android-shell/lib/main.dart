import 'dart:io';

import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:path_provider/path_provider.dart';
import 'package:share_plus/share_plus.dart';
import 'package:webview_flutter/webview_flutter.dart';
import 'package:webview_flutter_android/webview_flutter_android.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const AryaAdminApp());
}

class AryaAdminApp extends StatelessWidget {
  const AryaAdminApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'Arya手作 管理',
      theme: ThemeData(
        colorSchemeSeed: const Color(0xFFA98B84),
        useMaterial3: true,
      ),
      home: const WebShellPage(),
    );
  }
}

class WebShellPage extends StatefulWidget {
  const WebShellPage({super.key});

  @override
  State<WebShellPage> createState() => _WebShellPageState();
}

class _WebShellPageState extends State<WebShellPage> {
  late final WebViewController _controller;

  @override
  void initState() {
    super.initState();
    _controller = WebViewController()
      ..setJavaScriptMode(JavaScriptMode.unrestricted)
      ..setBackgroundColor(const Color(0xFFFAF6F0))
      // CSV 导出原生桥:JS 侧 window.exportCsv.postMessage("<文件名>\u0000<内容>")
      ..addJavaScriptChannel('exportCsv', onMessageReceived: _onExportCsv)
      ..setNavigationDelegate(
        NavigationDelegate(
          onWebResourceError: (e) {
            if (kDebugMode && e.isForMainFrame != false) {
              debugPrint('web error: ${e.description}');
            }
          },
        ),
      )
      ..loadFlutterAsset('webapp/index.html');

    final platform = _controller.platform;
    if (platform is AndroidWebViewController) {
      // 允许 WebView 内 video 自动/手动播放策略放宽
      platform.setMediaPlaybackRequiresUserGesture(false);
    }
    // 注:setWebContentsDebuggingEnabled 需 webview_flutter>=4.10,4.8.0 无此 API,
    // 如需 Chrome 远程调试请升级依赖后再启用。
  }

  Future<void> _onExportCsv(JavaScriptMessage msg) async {
    final i = msg.message.indexOf('\u0000');
    if (i < 0) return;
    final name = msg.message.substring(0, i);
    final data = msg.message.substring(i + 1);
    try {
      final dir = await getTemporaryDirectory();
      final file = File('${dir.path}/$name');
      await file.writeAsString(data);
      await Share.shareXFiles([XFile(file.path)], subject: name);
    } catch (e) {
      if (kDebugMode) debugPrint('export failed: $e');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFFAF6F0),
      body: SafeArea(
        top: false,
        bottom: false,
        child: WebViewWidget(controller: _controller),
      ),
    );
  }
}
