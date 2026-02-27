# BMAD: Breakthrough Method for Agile AI-Driven Development

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Documentation](https://img.shields.io/badge/docs-bmad--method.org-blue.svg)](https://docs.bmad-method.org)
[![GitHub](https://img.shields.io/badge/github-bmad--code--org%2FBMAD--METHOD-green.svg)](https://github.com/bmad-code-org/BMAD-METHOD)
[![Status](https://img.shields.io/badge/status-active-brightgreen.svg)](https://github.com/bmad-code-org/BMAD-METHOD)

*From chaos to clarity in AI-driven development.*

</div>

## 🚀 Overview

BMAD is an open-source, multi-agent framework that structures AI-assisted software development into a systematic, repeatable process. It combines traditional Agile methodologies with specialized AI agents to enhance productivity, consistency, and governance in software projects.

### 🎯 Mission Statement
Transform software development through systematic AI-human collaboration, where documentation drives implementation and specialized agents ensure consistent, predictable outcomes.

## 📋 Table of Contents

- [🚀 Overview](#-overview)
- [✨ Core Principles](#-core-principles)
- [🔄 The 4 Phases](#-the-4-phases)
- [👥 The 7 Agent Roles](#-the-7-agent-roles)
- [📊 BMAD vs Traditional Agile](#-bmad-vs-traditional-agile)
- [💡 Key Benefits](#-key-benefits)
- [🎨 Design Philosophy](#-design-philosophy)
- [📁 Project Structure](#-project-structure)
- [🛠️ Getting Started](#️-getting-started)
- [🔧 Installation](#-installation)
- [📚 Resources](#-resources)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)

## ✨ Core Principles

BMAD is built on three fundamental principles that guide its methodology:

### 1. Documentation as Source of Truth 📄
Documentation drives everything downstream. Code is a derivative artifact, ensuring consistency and traceability throughout the development lifecycle.

### 2. Agent-as-Code 🤖
AI agents defined as version-controlled Markdown files, enabling reproducible behavior and systematic improvements over time.

### 3. Structured Handoffs 🔄
Explicit artifacts prevent context loss between agents, maintaining continuity and reducing miscommunication.

## 🔄 The 4 Phases

BMAD follows a systematic cycle from idea to implementation:

```
Analysis → Planning → Solutioning → Implementation → (repeat)
```

| Phase | Input | Output | Primary Agent |
|-------|--------|---------|---------------|
| **Analysis** | Raw idea/concept | Project Brief | Analyst |
| **Planning** | Project Brief | PRD + Architecture | Product Manager + Architect |
| **Solutioning** | PRD + Architecture | Aligned Stories | Product Owner |
| **Implementation** | Detailed Stories | Code + Tests | Developer + QA Agent |

The process forms a continuous cycle that can be repeated as needed for iterative development.

## 👥 The 7 Agent Roles

BMAD employs specialized AI agents with distinct roles and responsibilities:

### 🎯 Planning Agents

#### **Analyst** 🔍
- **Role**: Explores idea space and surfaces constraints
- **Output**: Comprehensive project brief with requirements, constraints, and success criteria
- **Focus**: Understanding the problem domain and defining project boundaries

#### **Product Manager** 📋
- **Role**: Transforms brief into detailed PRD
- **Output**: Product Requirements Document with epics, user stories, and acceptance criteria
- **Focus**: Business value and user-centered design

#### **Architect** 🏗️
- **Role**: Designs full-stack system architecture
- **Output**: Architecture documents, component maps, data flow diagrams
- **Focus**: Technical feasibility and system design

#### **Product Owner** ✅
- **Role**: Aligns all documents and resolves conflicts
- **Output**: Synchronized project artifacts and master checklist
- **Focus**: Cross-functional alignment and quality assurance

### ⚙️ Execution Agents

#### **Scrum Master** 📊
- **Role**: Creates hyper-detailed implementation stories
- **Output**: Development-ready stories with embedded context and acceptance criteria
- **Focus**: Development team enablement and sprint planning

#### **Developer** 💻
- **Role**: Implements stories with comprehensive testing
- **Output**: Production-ready code, unit tests, and integration tests
- **Focus**: Code quality and implementation accuracy

#### **QA Agent** 🧪
- **Role**: Reviews stories and designs test cases
- **Output**: Test plans, quality assessments, and non-functional requirement evaluations
- **Focus**: Quality assurance and risk mitigation

## 📊 BMAD vs Traditional Agile

| Aspect | Traditional Agile | BMAD Method |
|--------|-------------------|-------------|
| **Team Composition** | Human-only team members | AI agents as specialized team members |
| **Source of Truth** | Source code | Documentation as source of truth |
| **Handoff Process** | Informal handoffs via meetings | Structured artifact handoffs |
| **Documentation** | Documentation is secondary | Documentation is first-class citizen |
| **Governance** | Governance added separately | Governance built into lifecycle |
| **Scalability** | Scales by hiring people | Scales instantly with AI agents |
| **Consistency** | Variable consistency | Consistent, predictable behavior |

## 💡 Key Benefits

### 🚀 **Eliminates Planning Bottlenecks**
AI agents generate PRDs and architecture docs with unprecedented precision, reducing planning phase from weeks to hours.

### 💰 **Cost Optimization**
Front-loaded planning concentrates tokens in high-value phases. Create once, reuse across multiple implementation cycles.

### 🔒 **Built-in Governance & Compliance**
Every decision is versioned and auditable. SOC 2, HIPAA compliance simplified through systematic documentation.

### 🎯 **Reduced Context Loss**
Structured handoffs with explicit artifacts prevent context evaporation between team transitions.

### 🛡️ **Security by Design**
Security requirements incorporated from the planning phase, not bolted on as an afterthought.

### ⚡ **Scales Instantly**
AI agents are always available and scale without hiring, onboarding, or training overhead.

## 🎨 Design Philosophy: Systematic Convergence

The visual materials in this project follow the "Systematic Convergence" design philosophy, which emphasizes:

- **Geometric Precision**: Clean lines, mathematical proportions, and chromatic restraint
- **Intentional Color Palettes**: Surgical color choices that enhance readability and visual hierarchy
- **Structural Typography**: Type that functions as both information carrier and visual form
- **Spatial Organization**: Layouts following the logic of convergent systems
- **Timeless Elegance**: Compositions that appear to have always existed in their refined form

## 📁 Project Structure

```
bmad-method/
├── create_bmad_presentation.py      # PDF generation script using ReportLab
├── bmad_design_philosophy.md        # Design philosophy documentation
├── BMAD_Beginners_Guide.pdf         # Comprehensive PDF guide
├── bmad-presentation/
│   └── index.html                   # Interactive HTML presentation
├── BMAD Beginner's Guide.pptx       # PowerPoint presentation
└── README.md                        # This file
```

## 🛠️ Getting Started

### Prerequisites
- Python 3.8+ (for presentation generation)
- Modern web browser (for HTML presentation)
- PDF viewer (for documentation)

### Quick Start
1. **Clone the repository**
   ```bash
   git clone https://github.com/bmad-code-org/BMAD-METHOD.git
   cd BMAD-METHOD
   ```

2. **Review the comprehensive guide**
   - Open `BMAD_Beginners_Guide.pdf` for detailed methodology overview
   - Explore `bmad-presentation/index.html` for interactive learning

3. **Generate custom presentations**
   ```bash
   python create_bmad_presentation.py
   ```

## 🔧 Installation

### For Development
```bash
# Clone the repository
git clone https://github.com/bmad-code-org/BMAD-METHOD.git
cd BMAD-METHOD

# Install dependencies (if any)
pip install -r requirements.txt  # If requirements.txt exists
```

### For Presentation Generation
```bash
# Install ReportLab for PDF generation
pip install reportlab

# Generate custom presentation
python create_bmad_presentation.py
```

## 📚 Resources

### 📖 Documentation
- **Comprehensive Docs**: [docs.bmad-method.org](https://docs.bmad-method.org)
- **Design Philosophy**: [bmad_design_philosophy.md](bmad_design_philosophy.md)
- **Beginner's Guide**: `BMAD_Beginners_Guide.pdf`

### 💻 Code & Community
- **GitHub Repository**: [github.com/bmad-code-org/BMAD-METHOD](https://github.com/bmad-code-org/BMAD-METHOD)
- **Issues & Discussions**: Use GitHub Issues for questions and suggestions
- **Contributions**: See [Contributing](#-contributing) section

### 🎯 Implementation Examples
- Review `create_bmad_presentation.py` for practical BMAD implementation
- Explore presentation files to understand systematic document generation

## 🤝 Contributing

BMAD is an open-source project that welcomes contributions from the community. Here's how you can help:

### 🌟 Ways to Contribute
- **Documentation**: Improve guides, add examples, fix typos
- **Code**: Enhance presentation generation, add new features
- **Methodology**: Suggest improvements to the BMAD process
- **Design**: Contribute to visual materials and presentations

### 📝 Contribution Process
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes and test thoroughly
4. Commit with clear messages (`git commit -m 'Add amazing feature'`)
5. Push to your branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request with detailed description

### 📋 Guidelines
- Follow existing code style and documentation patterns
- Add tests for new functionality
- Update documentation as needed
- Be respectful and constructive in discussions

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**🚀 The future of development is human + AI collaboration.**

*BMAD Method // Systematic Convergence Design // 2026*

[![Star History Chart](https://api.star-history.com/svg?repos=bmad-code-org/BMAD-METHOD&type=Date)](https://star-history.com/#bmad-code-org/BMAD-METHOD&Date)

</div>