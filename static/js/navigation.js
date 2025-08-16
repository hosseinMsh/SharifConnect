// Navigation and Page Management
import {Utils} from "./utils.js"
import {languageManager} from "./language.js"

export class NavigationManager {
    constructor() {
        this.currentPage = "login"
        this.isMenuOpen = false
        this.pageCache = new Map()
    }

    async init() {
        // Load menu component
        await this.loadMenu()

        // Initialize with login page
        await this.goToPage("login")
    }

    async loadMenu() {
        try {
            const menuHTML = await Utils.loadHTML("components/menu.html")
            const menuContainer = document.createElement("div")
            menuContainer.innerHTML = menuHTML
            document.body.appendChild(menuContainer.firstElementChild)
        } catch (error) {
            console.error("Failed to load menu:", error)
        }
    }

    async goToPage(pageName) {
        try {
            // Hide current page
            const currentPageElement = document.querySelector(".page.active")
            if (currentPageElement) {
                currentPageElement.classList.remove("active")
            }

            // Load page if not cached
            if (!this.pageCache.has(pageName)) {
                const pageHTML = await Utils.loadHTML(`pages/${pageName}.html`)
                this.pageCache.set(pageName, pageHTML)
            }

            // Update container content
            const container = document.getElementById("app-container")
            container.innerHTML = this.pageCache.get(pageName)

            // Add fade-in animation
            const newPageElement = container.querySelector(".page")
            if (newPageElement) {
                newPageElement.classList.add("active", "fade-in")
            }

            this.currentPage = pageName

            // Close menu if open
            if (this.isMenuOpen) {
                this.toggleMenu()
            }

            // Load page-specific data
            await this.loadPageData(pageName)

            // Update language
            languageManager.updateLanguage()
        } catch (error) {
            console.error("Failed to navigate to page:", error)
        }
    }

    async loadPageData(pageName) {
        try {
            switch (pageName) {
                case "dashboard":
                    await this.loadDashboardData()
                    break
                case "profile":
                    await this.loadProfileData()
                    break
                case "sessions":
                    await this.loadSessionsData()
                    break
                case "logs":
                    await this.loadLogsData()
                    break
                case "about":
                    await this.loadAboutData()
                    break
            }
        } catch (error) {
            console.error(`Failed to load data for ${pageName}:`, error)
        }
    }

    async loadDashboardData() {
        // Load initial dashboard data
        if (typeof window.pywebview !== "undefined") {
            try {
                const state = await window.pywebview.api.update_state()
                // Update connection status based on state
                this.updateConnectionStatus(state)
            } catch (error) {
                console.error("Failed to load dashboard data:", error)
            }
        }
    }

    async loadProfileData() {
        if (typeof window.pywebview !== "undefined") {
            try {
                const profile = await window.pywebview.api.profile()
                this.updateProfileDisplay(profile)
            } catch (error) {
                console.error("Failed to load profile data:", error)
            }
        }
    }

    async loadSessionsData() {
        if (typeof window.pywebview !== "undefined") {
            try {
                const sessions = await window.pywebview.api.sessions()
                this.updateSessionsDisplay(sessions)
            } catch (error) {
                console.error("Failed to load sessions data:", error)
            }
        }
    }

    async loadLogsData() {
        if (typeof window.pywebview !== "undefined") {
            try {
                const logs = await window.pywebview.api.get_logs()
                this.updateLogsDisplay(logs)
            } catch (error) {
                console.error("Failed to load logs data:", error)
            }
        }
    }

    async loadAboutData() {
        if (typeof window.pywebview !== "undefined") {
            try {
                const info = await window.pywebview.api.info()
                this.updateAboutDisplay(info)
            } catch (error) {
                console.error("Failed to load about data:", error)
            }
        }
    }

    updateConnectionStatus(state) {
        const statusIndicator = document.getElementById("status-indicator")
        const connectionText = document.getElementById("connection-text")

        if (statusIndicator && connectionText) {
            if (state === 2 || state === 3) {
                statusIndicator.className = "w-2 h-2 bg-sharif-green rounded-full"
                connectionText.textContent = "متصل"
            } else {
                statusIndicator.className = "w-2 h-2 bg-red-500 rounded-full"
                connectionText.textContent = "قطع شده"
            }
        }
    }

    updateProfileDisplay(profile) {
        const profileName = document.getElementById("profile-name")
        const profileDetails = document.getElementById("profile-details")

        if (profileName && profile.fullname) {
            const name = languageManager.currentLanguage === "en" ? profile.fullname_en : profile.fullname
            profileName.textContent = name
        }

        if (profileDetails) {
            profileDetails.innerHTML = `
                <h4 class="text-sm sm:text-base font-medium text-gray-800 mb-4" data-lang="subscription_details">جزئیات اشتراک</h4>
                <div class="space-y-3">
                    <div class="flex justify-between">
                        <span class="text-xs sm:text-sm text-gray-600" data-lang="username">نام کاربری</span>
                        <span class="text-xs sm:text-sm font-medium text-gray-800">${profile.username}</span>
                    </div>
                    <div class="flex justify-between">
                        <span class="text-xs sm:text-sm text-gray-600" data-lang="fullname">نام</span>
                        <span class="text-xs sm:text-sm font-medium text-gray-800">${profile.fullname || "نامشخص"}</span>
                    </div>
                    <div class="flex justify-between">
                        <span class="text-xs sm:text-sm text-gray-600" data-lang="gender">جنسیت</span>
                        <span class="text-xs sm:text-sm font-medium text-gray-800">${profile.gender || "نامشخص"}</span>
                    </div>
                    <div class="flex justify-between">
                        <span class="text-xs sm:text-sm text-gray-600" data-lang="mobile">تلفن همراه</span>
                        <span class="text-xs sm:text-sm font-medium text-gray-800">${profile.mobile || "نامشخص"}</span>
                    </div>
                    <div class="flex justify-between">
                        <span class="text-xs sm:text-sm text-gray-600" data-lang="account_status">وضعیت اکانت</span>
                        <span class="text-xs sm:text-sm font-medium text-gray-800">${profile.account_status}</span>
                    </div>
                </div>
            `
        }
    }

    updateSessionsDisplay(response) {
        const sessionsList = document.getElementById("sessions-list")
        if (!sessionsList) return

        // اگر نتیجه نداشت
        if (response.result === false) {
            sessionsList.innerHTML = '<p class="text-center text-gray-500 py-8">هیچ جلسه‌ای یافت نشد</p>'
            return
        }

        // گرفتن سشن‌ها (آرایه دوبل → [0])
        const sessions = response.data.result[0]
        const currentIp = response.data.ip


        sessionsList.innerHTML = sessions
            .map((session) => {
                const isCurrent = session.session_ip === currentIp

                return `
        <div class="bg-white rounded-xl p-4 shadow-sm border ${
                    isCurrent ? "border-green-500" : "border-gray-200"
                }">
          <div class="flex justify-between items-start mb-2">
            <span class="text-sm font-medium text-gray-800">
              Session ID: ${session.session_id}
            </span>
            <span class="text-xs px-2 py-1 rounded-full ${
                    isCurrent
                        ? "bg-green-100 text-green-800"
                        : "bg-yellow-100 text-yellow-800"
                }">
              ${isCurrent ? "Current" : "Active"}
            </span>
          </div>

          <div class="space-y-1 text-xs text-gray-600">
            <div class="flex justify-between">
              <span>آی‌پی کاربر:</span>
              <span>${session.session_ip || "-"}</span>
            </div>
            <div class="flex justify-between">
              <span>آی‌پی RAS:</span>
              <span>${session.ras_ip || "-"}</span>
            </div>
            <div class="flex justify-between">
              <span>زمان شروع:</span>
              <span>${session.session_start_time || "-"}</span>
            </div>
          </div>

          <div class="mt-3 text-right">
            <button 
              onclick="window.pywebview.api.disconnect_one_sessions('${session.ras_ip}', '${session.session_ip}', '${session.session_id}')"
              class="text-xs bg-red-100 text-red-600 px-3 py-1 rounded-lg hover:bg-red-200">
              Disconnect
            </button>
          </div>
        </div>
      `
            })
            .join("")

    }



    updateLogsDisplay(logs) {
        const logsList = document.getElementById("logs-list")
        if (!logsList) return

        logsList.innerHTML = logs
            .map(
                (log) => `
            <div class="flex items-center space-x-2 space-x-reverse">
                <span class="text-gray-500">${log.time}</span>
                <span class="w-2 h-2 rounded-full ${
                    log.type === "success" ? "bg-green-500" : log.type === "error" ? "bg-red-500" : "bg-blue-500"
                }"></span>
                <span class="flex-1">${log.message}</span>
            </div>
        `,
            )
            .join("")
    }

    updateAboutDisplay(info) {
        const appInfo = document.getElementById("app-info")
        if (!appInfo) return

        appInfo.innerHTML = `
            <div class="flex justify-between">
                <span class="text-xs sm:text-sm text-gray-600" data-lang="version">نسخه</span>
                <span class="text-xs sm:text-sm font-medium text-gray-800">${info.app_version}</span>
            </div>
            <div class="flex justify-between">
                <span class="text-xs sm:text-sm text-gray-600" data-lang="build_date">تاریخ ساخت</span>
                <span class="text-xs sm:text-sm font-medium text-gray-800">${info.build_date}</span>
            </div>
            <div class="flex justify-between">
                <span class="text-xs sm:text-sm text-gray-600" data-lang="platform">پلتفرم</span>
                <span class="text-xs sm:text-sm font-medium text-gray-800">${info.platform}</span>
            </div>
            <div class="flex justify-between">
                <span class="text-xs sm:text-sm text-gray-600" data-lang="server_status">وضعیت سرور</span>
                <span class="text-xs sm:text-sm font-medium text-sharif-green">${info.server_status}</span>
            </div>
            <div class="flex justify-between">
                <span class="text-xs sm:text-sm text-gray-600" data-lang="total_users">کل کاربران</span>
                <span class="text-xs sm:text-sm font-medium text-gray-800">${info.total_users}</span>
            </div>
        `
    }

    toggleMenu() {
        const menuOverlay = document.querySelector(".menu-overlay")
        const hamburgerMenu = document.querySelector(".hamburger-menu")

        if (menuOverlay && hamburgerMenu) {
            this.isMenuOpen = !this.isMenuOpen

            if (this.isMenuOpen) {
                menuOverlay.classList.add("active")
                hamburgerMenu.classList.add("active")
            } else {
                menuOverlay.classList.remove("active")
                hamburgerMenu.classList.remove("active")
            }
        }
    }
}

// Create and export global navigation manager instance
export const navigationManager = new NavigationManager()

// Global functions
window.goToPage = (pageName) => {
    navigationManager.goToPage(pageName)
}

window.toggleMenu = () => {
    navigationManager.toggleMenu()
}

window.loadSessions = (count) => {
    navigationManager.loadSessionsData(Number.parseInt(count))
}
