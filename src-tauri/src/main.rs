// Prevents additional console window on Windows in release
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use tauri::Manager;

#[cfg(not(debug_assertions))]
use std::sync::Mutex;

#[cfg(all(target_os = "windows", not(debug_assertions)))]
use std::os::windows::process::CommandExt;

#[cfg(all(target_os = "windows", not(debug_assertions)))]
const CREATE_NO_WINDOW: u32 = 0x08000000;

// 生产模式才需要管理进程句柄
#[cfg(not(debug_assertions))]
struct Backend(Mutex<Option<tauri_plugin_shell::process::CommandChild>>);

fn main() {
    #[cfg(not(debug_assertions))]
    let builder = tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_fs::init())
        .manage(Backend(Mutex::new(None)));

    #[cfg(debug_assertions)]
    let builder = tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_fs::init());

    builder
        .setup(|_app| {
            // 根据屏幕分辨率设置窗口为 80% 大小（考虑 DPI 缩放）
            if let Some(window) = _app.get_webview_window("main") {
                let _ = window.unmaximize();
                if let Ok(Some(screen)) = window.primary_monitor() {
                    let size = screen.size();
                    let scale = screen.scale_factor();
                    let w = ((size.width as f64 / scale) * 0.8) as f64;
                    let h = ((size.height as f64 / scale) * 0.8) as f64;
                    let _ = window.set_size(tauri::Size::Logical(tauri::LogicalSize::new(w, h)));
                    let _ = window.center();
                }
            }

            #[cfg(not(debug_assertions))]
            {
                // 生产模式：使用 sidecar 启动后端
                use tauri_plugin_shell::ShellExt;
                let shell = _app.shell();
                let sidecar_command = shell.sidecar("backend").expect("Failed to create sidecar command");
                let (_rx, child) = sidecar_command.spawn().expect("Failed to spawn sidecar");

                let backend = _app.state::<Backend>();
                *backend.0.lock().unwrap() = Some(child);

                std::thread::sleep(std::time::Duration::from_millis(500));
            }

            // 开发模式：server.py 已由 beforeDevCommand 启动，无需处理

            Ok(())
        })
        .build(tauri::generate_context!())
        .expect("error while building tauri application")
        .run(|_app_handle, event| {
            if let tauri::RunEvent::ExitRequested { .. } | tauri::RunEvent::Exit = event {
                #[cfg(not(debug_assertions))]
                {
                    let child_opt = {
                        let backend = _app_handle.state::<Backend>();
                        let child = backend.0.lock().unwrap().take();
                        child
                    };

                    if let Some(child) = child_opt {
                        // 使用 taskkill 杀死进程树，隐藏窗口
                        #[cfg(target_os = "windows")]
                        let _ = std::process::Command::new("taskkill")
                            .args(["/F", "/T", "/PID", &child.pid().to_string()])
                            .creation_flags(CREATE_NO_WINDOW)
                            .output();

                        let _ = child.kill();
                    }
                }
            }
        });
}
