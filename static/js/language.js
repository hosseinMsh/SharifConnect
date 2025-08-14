// Language Management
export class LanguageManager {
  constructor() {
    this.currentLanguage = "fa"
    this.languageData = {}
  }

  async init() {
    try {
      if (typeof window.pywebview !== "undefined") {
        const langData = await window.pywebview.api.get_language_data()
        this.currentLanguage = langData.current
        this.languageData = langData.data
      }
    } catch (error) {
      console.error("Failed to load language data:", error)
      // Fallback language data
      this.languageData = {
        app_name: "شریف کانکت",
        login: "ورود",
        username: "نام کاربری",
        password: "رمز عبور",
        dashboard: "داشبورد",
        settings: "تنظیمات",
        profile: "پروفایل",
        sessions: "جلسات",
        logs: "گزارش‌ها",
        about: "درباره ما",
        language: "زبان",
        disconnected: "قطع شده",
        connected: "متصل",
        full_protection: "حفاظت کامل",
        protection_desc: "اتصال شما رمزگذاری شده و امن است",
        secure_connection: "اتصال امن",
        unlimited_data: "داده نامحدود",
        server_location: "موقعیت سرور",
        your_ip: "آی‌پی شما",
        data_transferred: "داده منتقل شده",
        today: "امروز",
        this_week: "این هفته",
      }
    }
    this.updateLanguage()
  }

  async switchLanguage(langCode) {
    try {
      if (typeof window.pywebview !== "undefined") {
        const success = await window.pywebview.api.switch_language(langCode)
        if (success) {
          this.currentLanguage = langCode
          this.updateLanguage()
          this.updateDirection()
        }
      }
    } catch (error) {
      console.error("Failed to switch language:", error)
    }
  }

  updateLanguage() {
    const elements = document.querySelectorAll("[data-lang]")
    elements.forEach((element) => {
      const key = element.getAttribute("data-lang")
      if (this.languageData[key]) {
        element.textContent = this.languageData[key]
      }
    })

    // Update language buttons
    this.updateLanguageButtons()
  }

  updateDirection() {
    const body = document.body
    const html = document.documentElement

    if (this.currentLanguage === "fa") {
      body.classList.add("rtl")
      body.classList.remove("ltr")
      html.setAttribute("dir", "rtl")
      html.setAttribute("lang", "fa")
    } else {
      body.classList.add("ltr")
      body.classList.remove("rtl")
      html.setAttribute("dir", "ltr")
      html.setAttribute("lang", "en")
    }
  }

  updateLanguageButtons() {
    const faButtons = document.querySelectorAll("#lang-fa, #login-lang-fa")
    const enButtons = document.querySelectorAll("#lang-en, #login-lang-en")

    if (this.currentLanguage === "fa") {
      faButtons.forEach((btn) => {
        btn.className = "px-3 py-1 text-sm rounded-md bg-sharif-blue text-white"
      })
      enButtons.forEach((btn) => {
        btn.className = "px-3 py-1 text-sm rounded-md bg-gray-200 text-gray-700"
      })
    } else {
      faButtons.forEach((btn) => {
        btn.className = "px-3 py-1 text-sm rounded-md bg-gray-200 text-gray-700"
      })
      enButtons.forEach((btn) => {
        btn.className = "px-3 py-1 text-sm rounded-md bg-sharif-blue text-white"
      })
    }
  }
}

// Create and export global language manager instance
export const languageManager = new LanguageManager()

// Global function for switching language
window.switchLanguage = (langCode) => {
  languageManager.switchLanguage(langCode)
}
