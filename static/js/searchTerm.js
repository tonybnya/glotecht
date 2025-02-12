// Constants and Configuration
const CONFIG = {
  API_URL: "http://127.0.0.1:5003/api/terms/search",
  DEBOUNCE_DELAY: 300,
  COLORS: [
    { text: "text-white", bg: "bg-[#194B6B]" },
    { text: "text-white", bg: "bg-[#A32A34]" },
    { text: "text-white", bg: "bg-black" },
  ],
  SEARCH_TYPES: {
    term: { field: "english_term", altField: "french_term" },
    synonym: { field: "near_synonym_en", altField: "near_synonym_fr" },
    subdomain: {
      field: "subdomains_en",
      altField: "subdomains_fr",
      isArray: true,
    },
    lexical_relation: {
      field: "lexical_relations_en",
      altField: "lexical_relations_fr",
      isComplex: true,
    },
  },
};

// Text formatting utilities
const TextFormatter = {
  formatPatterns: {
    em: { pattern: /\<em\>(.*?)\<\/em\>/g, replacement: "<em>$1</em>" },
    sub: { pattern: /\<sub\>(.*?)\<\/sub\>/g, replacement: "<sub>$1</sub>" },
    u: {
      pattern: /\<u\>(.*?)\<\/u\>/g,
      replacement: '<span class="underline">$1</span>',
    },
    ms: {
      pattern: /\<ms\>(.*?)\<\/ms\>/g,
      replacement: '<span class="font-courier">$1</span>',
    },
    lt: {
      pattern: /\<lt\>(.*?)\<\/lt\>/g,
      replacement: '<span class="line-through">$1</span>',
    },
    b: { pattern: /\<b\>(.*?)\<\/b\>/g, replacement: "<strong>$1</strong>" },
  },

  format(text) {
    if (!text || typeof text !== "string") return "";

    return Object.values(this.formatPatterns).reduce(
      (formattedText, { pattern, replacement }) => {
        return formattedText.replace(pattern, replacement);
      },
      text
    );
  },
};

// Template rendering functions
const TemplateRenderer = {
  renderSubdomains(label, subdomains) {
    return subdomains
      .map((item, index) => {
        const color = CONFIG.COLORS[index % CONFIG.COLORS.length];
        return `<span class="inline-block ${color.bg} ${color.text} py-1 px-2 mr-1 mb-2 rounded-lg text-sm">${item}</span>`;
      })
      .join("");
  },

  renderField(label, value, isList = false) {
    if (!value || (Array.isArray(value) && value.length === 0)) return "";

    const formatValue = (item) => TextFormatter.format(item) || "<br />";

    const content = Array.isArray(value)
      ? isList
        ? `<ul class="list-none list-inside text-sm">
            ${value.map((item) => `<li>${formatValue(item)}</li>`).join("")}
          </ul>`
        : value
            .map(
              (item) => `<span class="mb-0 text-sm">${formatValue(item)}</span>`
            )
            .join("")
      : isList
      ? `<ul class="list-none list-inside text-sm">
            <li>${formatValue(value)}</li>
          </ul>`
      : `<p class="text-sm font-normal text-gray-900">${formatValue(
          value
        )}</p>`;

    return `
      <li class="py-3 sm:py-4">
        <div class="flex items-center space-x-4">
          <div class="flex-1 min-w-0">
            <p class="text-sm text-[#296F9A] font-bold">${label}</p>
            ${content}
          </div>
        </div>
      </li>`;
  },
  // renderField(label, value) {
  //   if (!value || (Array.isArray(value) && value.length === 0)) return '';

  //   const content = Array.isArray(value)
  //     ? value.map(item => `<span class="mb-0 text-sm">${TextFormatter.format(item) || '<br />'}</span>`).join('')
  //     : `<p class="text-sm font-normal text-gray-900">${TextFormatter.format(value)}</p>`;

  //   return `
  //     <li class="py-3 sm:py-4">
  //       <div class="flex items-center space-x-4">
  //         <div class="flex-1 min-w-0">
  //           <p class="text-sm text-[#296F9A] font-bold">${label}</p>
  //           ${content}
  //         </div>
  //       </div>
  //     </li>`;
  // },

  renderLexicalRelations(label, relations) {
    if (!relations?.length) return "";

    const tableRows = relations
      .map((relation) => {
        const [key, values] = Object.entries(relation)[0];
        const formattedValues = Array.isArray(values)
          ? values.map((value) => TextFormatter.format(value)).join("<br>")
          : TextFormatter.format(values || "");

        return `
        <tr>
          <th class="pl-0 py-2 text-sm font-normal">${TextFormatter.format(
            key
          )}</th>
          <td class="pl-0 py-2 text-sm">${formattedValues}</td>
        </tr>`;
      })
      .join("");

    return this.renderField(
      label,
      `
      <table class="table-auto text-sm w-full text-left whitespace-normal">
        ${tableRows}
      </table>`
    );
  },

  renderTermCard(item, isEnglish = true, fieldsToRender = {}) {
    const lang = isEnglish ? "en" : "fr";
    const labels = {
      semantic: isEnglish ? "Semantic Label" : "Etiquette Sémantique",
      domain: isEnglish ? "Domain" : "Domaine",
      subdomain: isEnglish ? "Subdomain" : "Sous-domaine",
      variant: isEnglish ? "Variant" : "Variante",
      synonym: isEnglish ? "Synonym" : "Synonyme",
      definition: isEnglish ? "Definition" : "Définition",
      syntactic: isEnglish
        ? "Syntactic Cooccurrence"
        : "Cooccurrence Syntaxique",
      lexical: isEnglish ? "Lexical Relations" : "Relations lexicales",
      confused: isEnglish
        ? "Not to be confused with"
        : "À ne pas confondre avec",
      expression: isEnglish ? "Frequent Expression" : "Expression fréquente",
      phraseology: isEnglish ? "Phraseology" : "Phraséologie",
      context: isEnglish ? "Context" : "Contexte",
    };

    const id = `${item.tid}-${lang}`;
    const fieldClass = `term-${item.tid}`; // Add this line to create a base class for the term

    return `
      <div id="${id}" class="bg-white shadow-sm rounded-md text-md h-full w-full p-6 ${fieldClass}-${lang}">
        <div class="flex flex-col items-start gap-1 mb-4">
          <div class="w-full flex justify-between items-center">
            <h3 class="text-xl max-sm:text-sm font-bold leading-none text-gray-500">
              <span class="text-[#A32A34] font-bold">${TextFormatter.format(
                item[`${lang === "en" ? "english" : "french"}_term`]
              )}</span>
            </h3>
            <button onclick="downloadTermAsPDF('${id}')" class="text-[#296F9A] hover:text-[#194B6B] transition-colors ml-2" title="Download as PDF">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </button>
          </div>
          <h4 class="text-gray-700 font-normal">
            <span class="text-[#296F9A]">${labels.semantic}</span>: ${
      item[`semantic_label_${lang}`]
    }
          </h4>
          <h4 class="text-gray-700">
            ${labels.domain}: <span class="text-[#296F9A] font-bold">${
      item[`domain_${lang}`]
    }</span>
          </h4>
          <h4 class="text-gray-700">
            ${labels.subdomain}: ${this.renderSubdomains(
      labels.subdomain,
      item[`subdomains_${lang}`]
    )}
          </h4>
        </div>
        <div class="flow-root">
          <ul role="list" class="divide-y divide-gray-200">
            ${
              fieldsToRender.variant?.[lang]
                ? this.renderField(
                    labels.variant,
                    item[`variant_${lang}`],
                    false,
                    `${fieldClass}-variant`
                  )
                : ""
            }
            ${
              fieldsToRender.synonym?.[lang]
                ? this.renderField(
                    labels.synonym,
                    item[`near_synonym_${lang}`],
                    false,
                    `${fieldClass}-synonym`
                  )
                : ""
            }
            ${
              fieldsToRender.definition?.[lang]
                ? this.renderField(
                    labels.definition,
                    item[`definition_${lang}`],
                    false,
                    `${fieldClass}-definition`
                  )
                : ""
            }
            ${
              fieldsToRender.syntactic?.[lang]
                ? this.renderField(
                    labels.syntactic,
                    item[`syntactic_cooccurrence_${lang}`],
                    true,
                    `${fieldClass}-syntactic`
                  )
                : ""
            }
            ${
              fieldsToRender.lexical?.[lang]
                ? this.renderLexicalRelations(
                    labels.lexical,
                    item[`lexical_relations_${lang}`],
                    `${fieldClass}-lexical`
                  )
                : ""
            }
            ${
              fieldsToRender.note?.[lang]
                ? this.renderField(
                    "Note",
                    item[`note_${lang}`],
                    false,
                    `${fieldClass}-note`
                  )
                : ""
            }
            ${
              fieldsToRender.confused?.[lang]
                ? this.renderField(
                    labels.confused,
                    item[`note_to_be_confused_with_${lang}`],
                    true,
                    `${fieldClass}-confused`
                  )
                : ""
            }
            ${
              fieldsToRender.expression?.[lang]
                ? this.renderField(
                    labels.expression,
                    item[`frequent_expression_${lang}`],
                    true,
                    `${fieldClass}-expression`
                  )
                : ""
            }
            ${
              fieldsToRender.phraseology?.[lang]
                ? this.renderField(
                    labels.phraseology,
                    item[`phraseology_${lang}`],
                    false,
                    `${fieldClass}-phraseology`
                  )
                : ""
            }
            ${
              fieldsToRender.context?.[lang]
                ? this.renderField(
                    labels.context,
                    item[`context_${lang}`],
                    false,
                    `${fieldClass}-context`
                  )
                : ""
            }
          </ul>
        </div>
      </div>`;
  },

  renderField(label, value, isList = false, fieldClass = "") {
    if (!value || (Array.isArray(value) && value.length === 0)) {
      return "";
    }

    const formatValue = (item) => TextFormatter.format(item) || "<br />";

    const content = Array.isArray(value)
      ? isList
        ? `<ul class="list-none list-inside text-sm">
            ${value.map((item) => `<li>${formatValue(item)}</li>`).join("")}
          </ul>`
        : value
            .map(
              (item) => `<span class="mb-0 text-sm">${formatValue(item)}</span>`
            )
            .join("")
      : isList
      ? `<ul class="list-none list-inside text-sm">
            <li>${formatValue(value)}</li>
          </ul>`
      : `<p class="text-sm font-normal text-gray-900">${formatValue(
          value
        )}</p>`;

    return `
      <li class="py-3 sm:py-4 ${fieldClass}">
        <div class="flex items-center space-x-4">
          <div class="flex-1 min-w-0">
            <p class="text-md text-[#296F9A] font-bold">${label}</p>
            ${content}
          </div>
        </div>
      </li>`;
  },

  renderLexicalRelations(label, relations, fieldClass = "") {
    if (!relations?.length) {
      return "";
    }

    const tableRows = relations
      .map((relation) => {
        const [key, values] = Object.entries(relation)[0];
        const formattedValues = Array.isArray(values)
          ? values.map((value) => TextFormatter.format(value)).join("<br>")
          : TextFormatter.format(values || "");

        return `
        <tr>
          <th class="pl-0 py-2 text-sm font-normal">${TextFormatter.format(
            key
          )}</th>
          <td class="pl-0 py-2 text-sm">${formattedValues}</td>
        </tr>`;
      })
      .join("");

    return this.renderField(
      label,
      `<table class="table-auto text-md w-full text-left whitespace-normal">
        ${tableRows}
      </table>`,
      false,
      fieldClass
    );
  },
};

// Search functionality
class SearchManager {
  constructor() {
    this.searchInput = document.getElementById("search-input");
    this.resultsContainer = document.getElementById("results");
    this.criteriaForm = document.getElementById("criteria-form");
    this.searchType = "term";
    this.debounceTimeout = null;

    if (!this.searchInput || !this.resultsContainer || !this.criteriaForm) {
      throw new Error("Required DOM elements are missing.");
    }

    this.init();
  }

  init() {
    this.searchInput.addEventListener("input", () => {
      clearTimeout(this.debounceTimeout);
      this.debounceTimeout = setTimeout(
        () => this.performSearch(),
        CONFIG.DEBOUNCE_DELAY
      );
    });

    // Listen for search type changes
    this.criteriaForm.addEventListener("change", (event) => {
      if (event.detail) {
        this.searchType = event.detail;
        this.performSearch();
      }
    });
  }

  async performSearch() {
    const searchTerm = this.searchInput.value.trim();
    if (!searchTerm) {
      this.resultsContainer.innerHTML = "";
      return;
    }

    try {
      const response = await fetch(
        `${CONFIG.API_URL}?q=${encodeURIComponent(searchTerm)}`,
        {
          headers: { Accept: "application/json" },
        }
      );

      if (!response.ok) {
        throw new Error("Quelque chose n'a pas marché.");
      }

      const data = await response.json();
      this.displayResults(data, searchTerm);
    } catch (error) {
      console.error("Error fetching data:", error);
      this.resultsContainer.innerHTML = `
        <p class="text-center">Vérifiez l'orthographe du terme et Réessayez !</p>`;
    }
  }

  displayResults(results, searchTerm) {
    if (results.length === 0) {
      this.resultsContainer.className =
        "w-full flex justify-center items-center min-h-[100px]";
      this.resultsContainer.innerHTML = `
        <div class="w-full flex justify-center items-center">
          <p class="text-center">Aucun résultat trouvé pour "${searchTerm}".</p>
        </div>`;
      return;
    }

    // Update container class for Swiper
    this.resultsContainer.className = "swiper w-full max-w-[95%] mx-auto";

    // Create Swiper structure
    this.resultsContainer.innerHTML = `
      <div class="swiper-wrapper">
        ${results
          .map((item) => {
            // Define field mappings with their corresponding API field names
            const fieldMappings = {
              variant: { en: "variant_en", fr: "variant_fr" },
              synonym: { en: "near_synonym_en", fr: "near_synonym_fr" },
              definition: { en: "definition_en", fr: "definition_fr" },
              syntactic: {
                en: "syntactic_cooccurrence_en",
                fr: "syntactic_cooccurrence_fr",
              },
              lexical: {
                en: "lexical_relations_en",
                fr: "lexical_relations_fr",
              },
              note: { en: "note_en", fr: "note_fr" },
              confused: {
                en: "note_to_be_confused_with_en",
                fr: "note_to_be_confused_with_fr",
              },
              expression: {
                en: "frequent_expression_en",
                fr: "frequent_expression_fr",
              },
              phraseology: { en: "phraseology_en", fr: "phraseology_fr" },
              context: { en: "context_en", fr: "context_fr" },
            };

            // Check each field's data presence
            const fieldsToRender = Object.entries(fieldMappings).reduce(
              (acc, [field, paths]) => {
                const hasEnData =
                  item[paths.en] &&
                  (!Array.isArray(item[paths.en]) || item[paths.en].length > 0);
                const hasFrData =
                  item[paths.fr] &&
                  (!Array.isArray(item[paths.fr]) || item[paths.fr].length > 0);

                // Only include fields that have data in at least one language
                if (hasEnData || hasFrData) {
                  acc[field] = { en: hasEnData, fr: hasFrData };
                }

                return acc;
              },
              {}
            );

            return `
            <div class="swiper-slide py-4">
              <div class="flex flex-col md:flex-row w-full gap-4">
                <article class="w-full md:w-1/2 p-4">
                  ${TemplateRenderer.renderTermCard(item, true, fieldsToRender)}
                </article>
                <article class="w-full md:w-1/2 p-4">
                  ${TemplateRenderer.renderTermCard(
                    item,
                    false,
                    fieldsToRender
                  )}
                </article>
              </div>
            </div>
          `;
          })
          .join("")}
      </div>
      <div class="swiper-pagination"></div>
      <div class="swiper-button-prev"></div>
      <div class="swiper-button-next"></div>
    `;

    // Initialize Swiper
    new Swiper(this.resultsContainer, {
      slidesPerView: 1,
      spaceBetween: 30,
      pagination: {
        el: ".swiper-pagination",
        clickable: true,
      },
      navigation: {
        nextEl: ".swiper-button-next",
        prevEl: ".swiper-button-prev",
      },
    });

    // Equalize heights after Swiper initialization
    results.forEach((item, index) => {
      const fields = [
        "variant",
        "synonym",
        "definition",
        "syntactic",
        "lexical",
        "note",
        "confused",
        "expression",
        "phraseology",
        "context",
      ];

      fields.forEach((field) => {
        const enSelector = `.term-${item.tid}-en .term-${item.tid}-${field}`;
        const frSelector = `.term-${item.tid}-fr .term-${item.tid}-${field}`;

        const enElement = document.querySelector(enSelector);
        const frElement = document.querySelector(frSelector);

        if (enElement && frElement) {
          enElement.style.height = "auto";
          frElement.style.height = "auto";
          const maxHeight = Math.max(
            enElement.offsetHeight,
            frElement.offsetHeight
          );
          enElement.style.height = `${maxHeight}px`;
          frElement.style.height = `${maxHeight}px`;
        }
      });
    });
  }
}

// Initialize search functionality when DOM is loaded
document.addEventListener("DOMContentLoaded", () => {
  try {
    new SearchManager();

    // Add PDF download functionality to window scope
    window.downloadTermAsPDF = async (termId) => {
      try {
        const termCard = document.getElementById(termId);
        if (!termCard) {
          console.error("Term card not found");
          return;
        }

        // Create a new window for the printable version
        const printWindow = window.open("", "_blank");
        printWindow.document.write(`
          <!DOCTYPE html>
          <html>
            <head>
              <title>Author: DT | Source: GLOTECHT @2024</title>
              <style>
                @media print {
                  @page {
                    margin: 20mm;
                    size: A4;
                  }
                }
                
                body {
                  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
                  line-height: 1.5;
                  color: #1a1a1a;
                  background: white;
                  margin: 0;
                  padding: 20px;
                }

                .term-card {
                  max-width: 210mm;
                  margin: 0 auto;
                  background: white;
                  padding: 2rem;
                  border-radius: 8px;
                  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
                }

                /* Typography */
                h3 {
                  font-size: 1.5rem;
                  margin-bottom: 1rem;
                  color: #333;
                }

                h4 {
                  font-size: 1rem;
                  margin: 0.5rem 0;
                  color: #4a4a4a;
                }

                .text-[#A32A34] {
                  color: #A32A34;
                }

                .text-[#296F9A] {
                  color: #296F9A;
                }

                /* Term specific styling */
                .font-bold {
                  font-weight: 600;
                }

                /* Tags/Labels */
                .rounded-lg {
                  border-radius: 6px;
                }

                /* Subdomain tags */
                .bg-[#194B6B] { background-color: #194B6B; }
                .bg-[#A32A34] { background-color: #A32A34; }
                .bg-black { background-color: black; }
                .text-white { color: white; }

                .inline-block {
                  display: inline-block;
                  padding: 0.25rem 0.75rem;
                  margin: 0 0.25rem 0.5rem 0;
                }

                /* List styling */
                ul {
                  list-style: none;
                  padding: 0;
                  margin: 1rem 0;
                }

                li {
                  padding: 0.75rem 0;
                  border-bottom: 1px solid #eaeaea;
                }

                li:last-child {
                  border-bottom: none;
                }

                /* Table styling */
                table {
                  width: 100%;
                  border-collapse: collapse;
                  margin: 1rem 0;
                }

                th, td {
                  text-align: left;
                  padding: 0.75rem 0;
                  border-bottom: 1px solid #eaeaea;
                }

                /* Text formatting */
                em { font-style: italic; }
                strong { font-weight: 600; }
                .underline { text-decoration: underline; }
                .font-courier { font-family: "Courier New", monospace; }
                .line-through { text-decoration: line-through; }

                /* Remove print-unfriendly elements */
                button, .download-btn {
                  display: none !important;
                }

                /* Header section */
                .term-header {
                  margin-bottom: 2rem;
                  padding-bottom: 1rem;
                  border-bottom: 2px solid #eaeaea;
                }

                /* Content sections */
                .term-section {
                  margin: 1rem 0;
                }

                .term-label {
                  color: #296F9A;
                  font-weight: 600;
                  margin-bottom: 0.5rem;
                }

                /* Print optimization */
                @media print {
                  .term-card {
                    box-shadow: none;
                    padding: 0;
                  }

                  body {
                    padding: 0;
                  }
                }
              </style>
            </head>
            <body>
              <div class="term-card">
                ${termCard.innerHTML}
              </div>
            </body>
          </html>
        `);

        printWindow.document.close();
        printWindow.focus();

        // Wait for content and styles to load
        setTimeout(() => {
          printWindow.print();
          printWindow.close();
        }, 500);
      } catch (error) {
        console.error("Error generating PDF:", error);
      }
    };
  } catch (error) {
    console.error("Failed to initialize search:", error);
  }
});
