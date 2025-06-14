// Constants and Configuration
// Update the SEARCH_TYPES configuration
const CONFIG = {
  API_URL: "/api/terms/search",
  DEBOUNCE_DELAY: 300,
  COLORS: [
    { text: "text-white", bg: "bg-[#194B6B]" },
    { text: "text-white", bg: "bg-[#A32A34]" },
    { text: "text-white", bg: "bg-black" },
  ],
  SEARCH_TYPES: {
    term: { 
      field: "english_term", 
      altField: "french_term",
      exact: true 
    },
    semantic_label: { 
      field: "semantic_label_en", 
      altField: "semantic_label_fr",
      exact: false
    },
    synonym: { 
      field: "synonym_en", 
      altField: "synonym_fr",
      exact: false
    },
    relations: { 
      field: "semantic_label_en", 
      altField: "semantic_label_fr",
      exact: false,
      backendType: "class"
    },
    subdomain: {
      field: "subdomains_en",
      altField: "subdomains_fr",
      isArray: true,
      exact: false,
      values: {
        en: ['Artificial Intelligence', 'Big Data', 'Blockchain'],
        fr: ['Intelligence Artificielle', 'Big Data', 'Blockchain']
      }
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
      replacement: '<span class="font-mono">$1</span>',
      // replacement: '<span class="font-courier">$1</span>',
    },
    lt: {
      pattern: /\<lt\>(.*?)\<\/lt\>/g,
      replacement: '<span class="line-through">$1</span>',
    },
    b: { pattern: /\<b\>(.*?)\<\/b\>/g, replacement: "<strong>$1</strong>" },
    sup: { pattern: /<sup>(.*?)<\/sup>/g, replacement: "<sup>$1</sup>" },
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
      near_synonym: isEnglish ? "Near Synonym" : "Quasi-synonyme",
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
        <div class="term-header flex flex-col items-start gap-1 mb-4">
          <div class="w-full flex justify-between items-center">
            <h3 class="text-md max-sm:text-sm font-bold leading-none text-gray-500">
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
                    item[`synonym_${lang}`],
                    false,
                    `${fieldClass}-synonym`
                  )
                : ""
            }
            ${
              fieldsToRender.near_synonym?.[lang]
                ? this.renderField(
                    labels.near_synonym,
                    item[`near_synonym_${lang}`],
                    false,
                    `${fieldClass}-near_synonym`
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
                    item[`not_to_be_confused_with_${lang}`],
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
    console.log("SearchManager constructor called.");
    this.searchInput = document.getElementById("search-input");
    this.resultsContainer = document.getElementById("results");
    this.criteriaForm = document.getElementById("criteria-form");
    this.searchCriteria = document.getElementById("search-criteria");
    this.searchButton = document.getElementById("search-button");
    console.log("DOM elements:", {
      searchInput: !!this.searchInput,
      resultsContainer: !!this.resultsContainer,
      criteriaForm: !!this.criteriaForm,
      searchCriteria: !!this.searchCriteria,
      searchButton: !!this.searchButton,
    });

    this.searchType = this.searchCriteria ? this.searchCriteria.value : "term";
    this.debounceTimeout = null;

    if (!this.searchInput || !this.resultsContainer) {
      console.error("Required DOM elements are missing. Search functionality will not initialize.");
      return;
    }

    this.init();
  }

  init() {
    console.log("SearchManager init() called.");
    // Handle input changes with debounce
    this.searchInput.addEventListener("input", () => {
      clearTimeout(this.debounceTimeout);
      this.debounceTimeout = setTimeout(
        () => this.performSearch(),
        CONFIG.DEBOUNCE_DELAY
      );
    });

    // Handle search criteria changes
    if (this.searchCriteria) {
      this.searchCriteria.addEventListener("change", (event) => {
        this.searchType = event.target.value;
        console.log("Search criteria changed to:", this.searchType);
        this.updatePlaceholder(); // Update placeholder on change
        // Don't auto-search on mobile when criteria changes
        if (window.innerWidth > 768) {
          this.performSearch();
        }
      });
    }

    // Handle form submission
    if (this.criteriaForm) {
      this.criteriaForm.addEventListener("submit", (event) => {
        console.log("Search form submitted.");
        event.preventDefault();
        this.performSearch();
      });
    }

    // Add search button click handler
    if (this.searchButton) {
      this.searchButton.addEventListener("click", (event) => {
        console.log("Search button clicked.");
        event.preventDefault();
        this.performSearch();
      });
    }

    // Handle enter key in search input
    this.searchInput.addEventListener('keypress', (event) => {
      if (event.key === 'Enter') {
        console.log("Enter key pressed in search input.");
        event.preventDefault();
        this.performSearch();
      }
    });

    // Make performSearch available globally for external calls
    window.performSearch = (type, term) => {
      console.log("window.performSearch called with type:", type, "and term:", term);
      if (type) this.searchType = type;
      if (term) this.searchInput.value = term;
      this.performSearch();
    };

    // Set initial placeholder
    this.updatePlaceholder();
  }

  // Add method to update placeholder
  updatePlaceholder() {
    console.log("updatePlaceholder() called.");
    const selectedValue = this.searchCriteria.value;
    console.log("Selected search criteria value:", selectedValue);
    let placeholderText = "Rechercher...";

    switch (selectedValue) {
      case 'term':
        placeholderText = "Rechercher un terme...";
        break;
      case 'subdomain':
        placeholderText = "Ex: Artificial Intelligence, Intelligence Artificielle...";
        break;
      case 'synonym':
        placeholderText = "Ex: metaverse, fork...";
        break;
      case 'relations': // Assuming 'relations' maps to semantic_label search type
        placeholderText = "Ex: action sur les données, network attack...";
        break;
      default:
        placeholderText = "Rechercher...";
    }
    this.searchInput.placeholder = placeholderText;
  }

  // Update the performSearch method in SearchManager class
  async performSearch() {
    console.log("performSearch() called.");
    const searchTerm = this.searchInput.value.trim();
    if (!searchTerm) {
      this.resultsContainer.innerHTML = "";
      return;
    }

    try {
      // Get the current search type from the select element
      if (this.searchCriteria) {
        this.searchType = this.searchCriteria.value;
      }
      
      const searchConfig = CONFIG.SEARCH_TYPES[this.searchType];
      if (!searchConfig) {
        console.error("Invalid search type:", this.searchType);
        throw new Error("Type de recherche invalide");
      }

      // Show loading indicator
      this.resultsContainer.innerHTML = `
        <div class="w-full flex justify-center items-center min-h-[100px]">
          <p class="text-center">Recherche en cours...</p>
        </div>`;

      const params = new URLSearchParams({
        q: searchTerm,
        type: searchConfig.backendType || this.searchType,
        exact: searchConfig.exact || false,
        field: searchConfig.field,
        altField: searchConfig.altField,
        isArray: searchConfig.isArray || false
      });

      const response = await fetch(`${CONFIG.API_URL}?${params}`, {
        headers: { Accept: "application/json" },
      });

      if (!response.ok) {
        throw new Error(`Erreur serveur: ${response.status}`);
      }

      const data = await response.json();
      this.displayResults(data, searchTerm);
    } catch (error) {
      console.error("Error fetching data:", error);
      this.resultsContainer.innerHTML = `
        <div class="w-full flex justify-center items-center min-h-[100px]">
          <p class="text-center text-red-600">Une erreur s'est produite. Veuillez réessayer.</p>
          <p class="text-center text-gray-500 text-sm mt-2">${error.message}</p>
        </div>`;
    }
  }

  displayResults(results, searchTerm) {
    console.log("displayResults() called with results:", results, "for term:", searchTerm);
    if (results.length === 0) {
      this.resultsContainer.className =
        "w-full flex justify-center items-center min-h-[100px]";
      this.resultsContainer.innerHTML = `
        <div class="w-full flex justify-center items-center">
          <p class="text-center">Aucun résultat trouvé pour "${searchTerm}".</p>
        </div>`;
      return;
    }

    // Reset container class - changed from grid to flex layout with full width
    this.resultsContainer.className = "w-full my-4 px-4 max-w-full";

    // Constants for pagination - changed to 1 item per page
    const ITEMS_PER_PAGE = 1;
    let currentPage = 1;
    const totalPages = Math.ceil(results.length / ITEMS_PER_PAGE);

    // Function to render a specific page of results
    const renderPage = (pageNum) => {
      // Calculate start and end indices for the current page
      const startIndex = (pageNum - 1) * ITEMS_PER_PAGE;
      const endIndex = Math.min(startIndex + ITEMS_PER_PAGE, results.length);
      const pageResults = results.slice(startIndex, endIndex);

      // Clear the results container
      this.resultsContainer.innerHTML = '';

      // Remove any existing pagination
      const existingPagination = document.getElementById('search-pagination-container');
      if (existingPagination) {
        existingPagination.remove();
      }

      // Render each result for the current page (now just one item)
      pageResults.forEach(item => {
        // Define field mappings with their corresponding API field names
        const fieldMappings = {
          variant: { en: "variant_en", fr: "variant_fr" },
          synonym: { en: "synonym_en", fr: "synonym_fr" },
          near_synonym: { en: "near_synonym_en", fr: "near_synonym_fr" },
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
            en: "not_to_be_confused_with_en",
            fr: "not_to_be_confused_with_fr",
          },
          expression: {
            en: "frequent_expression_en",
            fr: "frequent_expression_fr",
          },
          phraseology: { en: "phraseology_en", fr: "phraseology_fr" },
          context: { en: "context_en", fr: "context_fr" },
        };

        // Build a filtered fieldsToRender object
        const isNonEmpty = (val) =>
          val && (
            (Array.isArray(val) && val.length > 0) ||
            (typeof val === "string" && val.trim().length > 0)
          );

        const fieldsToRender = Object.entries(fieldMappings).reduce(
          (acc, [field, paths]) => {
            const hasEnData = isNonEmpty(item[paths.en]);
            const hasFrData = isNonEmpty(item[paths.fr]);
            if (hasEnData || hasFrData) {
              acc[field] = { en: hasEnData, fr: hasFrData };
            }
            return acc;
          },
          {}
        );

        // Create a container for this result - updated for better width control
        const resultContainer = document.createElement('div');
        resultContainer.className = 'flex flex-col md:flex-row w-full gap-6 mb-8';
        resultContainer.innerHTML = `
          <article class="w-full md:w-1/2 flex-1">
            ${TemplateRenderer.renderTermCard(item, true, fieldsToRender)}
          </article>
          <article class="w-full md:w-1/2 flex-1">
            ${TemplateRenderer.renderTermCard(item, false, fieldsToRender)}
          </article>
        `;

        this.resultsContainer.appendChild(resultContainer);

        // Equalize header heights
        const enHeader = resultContainer.querySelector('.term-header');
        const frHeader = resultContainer.querySelectorAll('.term-header')[1];
        if (enHeader && frHeader) {
          enHeader.style.height = 'auto';
          frHeader.style.height = 'auto';
          const maxHeaderHeight = Math.max(enHeader.offsetHeight, frHeader.offsetHeight);
          enHeader.style.height = `${maxHeaderHeight}px`;
          frHeader.style.height = `${maxHeaderHeight}px`;
        }
      });

      // Create pagination container
      const paginationContainer = document.createElement('div');
      paginationContainer.id = 'search-pagination-container';
      paginationContainer.className = 'flex flex-col items-center space-y-2 mt-6 mb-8 w-full';
      
      // Add result counter
      const resultCounter = document.createElement('div');
      resultCounter.className = 'text-sm text-gray-500 mb-2';
      resultCounter.textContent = `Résultat ${currentPage} sur ${totalPages}`;
      paginationContainer.appendChild(resultCounter);

      // Create pagination buttons container
      const paginationButtons = document.createElement('div');
      paginationButtons.className = 'flex justify-center items-center space-x-2';
      
      // Previous button
      const prevButton = document.createElement('button');
      prevButton.className = `px-3 py-1 rounded-md ${currentPage === 1 ? 'bg-gray-100 text-gray-400 cursor-not-allowed' : 'bg-gray-100 hover:bg-gray-200 text-gray-700'}`;
      prevButton.innerHTML = '&larr;';
      prevButton.disabled = currentPage === 1;
      prevButton.onclick = () => {
        if (currentPage > 1) {
          currentPage--;
          renderPage(currentPage);
        }
      };
      paginationButtons.appendChild(prevButton);

      // Page numbers - show limited page numbers with ellipsis for better UX
      const maxVisiblePages = 5;
      let startPage = Math.max(1, currentPage - Math.floor(maxVisiblePages / 2));
      let endPage = Math.min(totalPages, startPage + maxVisiblePages - 1);
      
      if (endPage - startPage + 1 < maxVisiblePages) {
        startPage = Math.max(1, endPage - maxVisiblePages + 1);
      }
      
      // First page button if not visible
      if (startPage > 1) {
        const firstPageButton = document.createElement('button');
        firstPageButton.className = 'page-button px-3 py-1 rounded-md hover:bg-gray-200';
        firstPageButton.textContent = '1';
        firstPageButton.dataset.page = 1;
        firstPageButton.onclick = () => {
          currentPage = 1;
          renderPage(currentPage);
        };
        paginationButtons.appendChild(firstPageButton);
        
        // Add ellipsis if needed
        if (startPage > 2) {
          const ellipsis = document.createElement('span');
          ellipsis.textContent = '...';
          ellipsis.className = 'px-1';
          paginationButtons.appendChild(ellipsis);
        }
      }
      
      // Page numbers
      for (let i = startPage; i <= endPage; i++) {
        const pageButton = document.createElement('button');
        pageButton.className = `page-button px-3 py-1 rounded-md hover:bg-gray-200 ${i === currentPage ? 'bg-gray-200 font-bold' : ''}`;
        pageButton.textContent = i;
        pageButton.dataset.page = i;
        pageButton.onclick = () => {
          currentPage = i;
          renderPage(currentPage);
        };
        paginationButtons.appendChild(pageButton);
      }
      
      // Last page button if not visible
      if (endPage < totalPages) {
        // Add ellipsis if needed
        if (endPage < totalPages - 1) {
          const ellipsis = document.createElement('span');
          ellipsis.textContent = '...';
          ellipsis.className = 'px-1';
          paginationButtons.appendChild(ellipsis);
        }
        
        const lastPageButton = document.createElement('button');
        lastPageButton.className = 'page-button px-3 py-1 rounded-md hover:bg-gray-200';
        lastPageButton.textContent = totalPages;
        lastPageButton.dataset.page = totalPages;
        lastPageButton.onclick = () => {
          currentPage = totalPages;
          renderPage(currentPage);
        };
        paginationButtons.appendChild(lastPageButton);
      }

      // Next button
      const nextButton = document.createElement('button');
      nextButton.className = `px-3 py-1 rounded-md ${currentPage === totalPages ? 'bg-gray-100 text-gray-400 cursor-not-allowed' : 'bg-gray-100 hover:bg-gray-200 text-gray-700'}`;
      nextButton.innerHTML = '&rarr;';
      nextButton.disabled = currentPage === totalPages;
      nextButton.onclick = () => {
        if (currentPage < totalPages) {
          currentPage++;
          renderPage(currentPage);
        }
      };
      paginationButtons.appendChild(nextButton);

      // Add pagination buttons to the container
      paginationContainer.appendChild(paginationButtons);

      // Add pagination to the page
      document.getElementById('main-content').appendChild(paginationContainer);

      // Equalize heights after rendering
      pageResults.forEach((item) => {
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
    };

    // Initial render of the first page
    renderPage(1);
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
              <title>Author: DT | Source: GLOTECHT @${new Date().getFullYear()}</title>
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
