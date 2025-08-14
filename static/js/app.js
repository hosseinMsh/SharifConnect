// Main Application
import { Utils } from "./utils.js"
import { languageManager } from "./language.js"
import { navigationManager } from "./navigation.js"

class SharifConnectApp {
  constructor() {
    this.isConnected = false
    this.isLoggedIn = false
    this.connectionState = -1
  }

  async init() {
    try {
      // Initialize language manager
      await languageManager.init()

      // Initialize navigation manager
      await navigationManager.init()

      // Check if pywebview is available
      if (typeof window.pywebview !== "undefined") {
        // Load initial configuration
        await this.loadInitialConfig()

        // Check login status
        await this.checkLoginStatus()
      } else {
        // Development mode - show login
        await navigationManager.goToPage("login")
      }

      // Start periodic updates
      this.startPeriodicUpdates()
    } catch (error) {
      console.error("Failed to initialize app:", error)
      await navigationManager.goToPage("login")
    }
  }

  async loadInitialConfig() {
    try {
      const config = await window.pywebview.api.config_data()
      if (config.username && config.password) {
        const usernameField = document.getElementById("username")
        const passwordField = document.getElementById("password")
        if (usernameField) usernameField.value = config.username
        if (passwordField) passwordField.value = config.password
      }
    } catch (error) {
      console.error("Failed to load config:", error)
    }
  }

  async checkLoginStatus() {
    try {
      // This would need to be implemented in the Python API
      // For now, assume not logged in
      this.isLoggedIn = false
      await navigationManager.goToPage("login")
    } catch (error) {
      console.error("Failed to check login status:", error)
      await navigationManager.goToPage("login")
    }
  }

  async handleLogin(event) {
    event.preventDefault()

    const username = document.getElementById("username").value
    const password = document.getElementById("password").value
    const errorDiv = document.getElementById("login-error")

    try {
      const result = await window.pywebview.api.login(username, password, true)

      if (result.success) {
        this.isLoggedIn = true
        await navigationManager.goToPage("dashboard")
        errorDiv.classList.add("hidden")
        Utils.showNotification("ورود موفقیت‌آمیز بود", "success")
      } else {
        errorDiv.textContent = result.message
        errorDiv.classList.remove("hidden")
        Utils.showNotification("خطا در ورود", "error")
      }
    } catch (error) {
      console.error("Login failed:", error)
      errorDiv.textContent = "خطا در ورود به سیستم"
      errorDiv.classList.remove("hidden")
      Utils.showNotification("خطا در ورود به سیستم", "error")
    }
  }

  async toggleConnection(toggleElement) {
    if (!this.isLoggedIn) {
      Utils.showNotification("لطفا ابتدا وارد شوید", "error")
      return
    }

    try {
      if (this.isConnected) {
        const result = await window.pywebview.api.disconnect()
        if (result.success) {
          this.isConnected = false
          this.updateConnectionUI(false)
          Utils.showNotification("اتصال قطع شد", "info")
        }
      } else {
        const result = await window.pywebview.api.connect()
        if (result.success) {
          this.isConnected = true
          this.updateConnectionUI(true)
          Utils.showNotification("اتصال برقرار شد", "success")

          // Update IP address
          const currentIpElement = document.getElementById("current-ip")
          if (currentIpElement && result.ip) {
            currentIpElement.textContent = `آی‌پی شما: ${result.ip}`
          }
        }
      }
    } catch (error) {
      console.error("Connection toggle failed:", error)
      Utils.showNotification("خطا در تغییر وضعیت اتصال", "error")
    }
  }

  updateConnectionUI(connected) {
    const toggleElement = document.getElementById("main-toggle")
    const statusIndicator = document.getElementById("status-indicator")
    const connectionText = document.getElementById("connection-text")
    const protectionCircle = document.getElementById("protection-circle")

    if (toggleElement) {
      const toggleButton = toggleElement.querySelector("div")
      if (connected) {
        toggleElement.classList.add("active")
        if (toggleButton) toggleButton.style.transform = "translateX(-1.5rem)"
      } else {
        toggleElement.classList.remove("active")
        if (toggleButton) toggleButton.style.transform = "translateX(0)"
      }
    }

    if (statusIndicator) {
      statusIndicator.className = connected ? "w-2 h-2 bg-sharif-green rounded-full" : "w-2 h-2 bg-red-500 rounded-full"
    }

    if (connectionText) {
      connectionText.textContent = connected ? "متصل" : "قطع شده"
    }

    if (protectionCircle) {
      protectionCircle.className = connected
        ? "w-24 h-24 sm:w-32 sm:h-32 lg:w-40 lg:h-40 border-4 border-sharif-green rounded-full flex items-center justify-center bg-white shadow-lg"
        : "w-24 h-24 sm:w-32 sm:h-32 lg:w-40 lg:h-40 border-4 border-gray-300 rounded-full flex items-center justify-center bg-white shadow-lg"
    }
  }

  async toggleSetting(toggleElement, settingName = null) {
    const isActive = toggleElement.classList.contains("active")

    if (isActive) {
      toggleElement.classList.remove("active")
      const toggleButton = toggleElement.querySelector("div")
      if (toggleButton) toggleButton.style.transform = "translateX(0)"
    } else {
      toggleElement.classList.add("active")
      const toggleButton = toggleElement.querySelector("div")
      if (toggleButton) toggleButton.style.transform = "translateX(-1.5rem)"
    }

    // Save setting if pywebview is available
    if (typeof window.pywebview !== "undefined" && settingName) {
      try {
        const settings = {}
        settings[settingName] = !isActive
        await window.pywebview.api.update_settings(settings)
      } catch (error) {
        console.error("Failed to update setting:", error)
      }
    }
  }

  async handleChangeCredentials(event) {
    event.preventDefault()

    const currentPassword = document.getElementById("current-password").value
    const newUsername = document.getElementById("new-username").value
    const newPassword = document.getElementById("new-password").value
    const resultDiv = document.getElementById("change-result")

    try {
      const result = await window.pywebview.api.change(newUsername, newPassword, currentPassword)

      if (result.success) {
        resultDiv.textContent = result.message
        resultDiv.className = "mt-2 text-sm text-center text-green-600"
        resultDiv.classList.remove("hidden")

        // Clear form
        event.target.reset()

        Utils.showNotification("اطلاعات با موفقیت به‌روزرسانی شد", "success")
      } else {
        resultDiv.textContent = result.message
        resultDiv.className = "mt-2 text-sm text-center text-red-600"
        resultDiv.classList.remove("hidden")

        Utils.showNotification("خطا در به‌روزرسانی اطلاعات", "error")
      }
    } catch (error) {
      console.error("Failed to change credentials:", error)
      resultDiv.textContent = "خطا در به‌روزرسانی اطلاعات"
      resultDiv.className = "mt-2 text-sm text-center text-red-600"
      resultDiv.classList.remove("hidden")

      Utils.showNotification("خطا در به‌روزرسانی اطلاعات", "error")
    }
  }

  startPeriodicUpdates() {
    // Update data usage every 5 seconds when connected
    setInterval(() => {
      if (this.isConnected) {
        this.updateDataUsage()
      }
    }, 5000)

    // Update connection state every 10 seconds
    setInterval(() => {
      if (this.isLoggedIn) {
        this.updateConnectionState()
      }
    }, 10000)
  }

  updateDataUsage() {
    const todayData = document.getElementById("today-data")
    const weekData = document.getElementById("week-data")

    if (todayData && weekData) {
      const currentMB = Number.parseInt(todayData.textContent) || 0
      const currentGB = Number.parseFloat(weekData.textContent) || 0

      todayData.textContent = currentMB + Math.floor(Math.random() * 10) + " MB"
      weekData.textContent = (currentGB + Math.random() * 0.1).toFixed(1) + " GB"
    }
  }

  async updateConnectionState() {
    try {
      if (typeof window.pywebview !== "undefined") {
        const state = await window.pywebview.api.update_state()
        this.connectionState = state
        navigationManager.updateConnectionStatus(state)
      }
    } catch (error) {
      console.error("Failed to update connection state:", error)
    }
  }
}

// Global app instance
const app = new SharifConnectApp()

// Global functions for HTML event handlers
window.handleLogin = (event) => {
  app.handleLogin(event)
}

window.toggleConnection = (toggleElement) => {
  app.toggleConnection(toggleElement)
}

window.toggleSetting = (toggleElement, settingName) => {
  app.toggleSetting(toggleElement, settingName)
}

window.handleChangeCredentials = (event) => {
  app.handleChangeCredentials(event)
}

// Initialize app when DOM is loaded
document.addEventListener("DOMContentLoaded", () => {
  app.init()
})

// Initialize app when pywebview is ready
if (typeof window !== "undefined") {
  window.addEventListener("pywebviewready", () => {
    app.loadInitialConfig()
  })
}
