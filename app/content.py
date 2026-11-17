"""Editable organisational content. Wording follows the supplied PCPHI information."""
ORG = {
    "name": "Participative Care Public Health Initiative", "short": "PCPHI",
    "tagline": "Building Healthier Communities Through Participation.",
    "lead": "We work alongside communities, partners and institutions to improve health outcomes, strengthen prevention and create sustainable public health solutions.",
    "vision": "To build a healthier and empowered society through meaningful community engagement and improved health outcomes for all.",
    "mission": "To improve health outcomes through community-driven approaches that strengthen prevention, health literacy, equitable healthcare access and sustainable public health solutions.",
    "overview": "Participative Care Public Health Initiative (PCPHI) is an active, community-focused non-governmental organisation that aims to enhance public health through inclusive and participatory methods.",
    "founded": "Founded to tackle urgent health issues, PCPHI is dedicated to empowering communities by encouraging collaboration, education and sustainable health interventions.",
    "work": "The organisation works in the development and humanitarian sector, supporting real-time efforts to address fundamental health issues and challenges faced by vulnerable populations, people living with HIV and key populations.",
    "activities": "Its activities include screening, health education, community interventions and other public health activities in developing countries.",
    "partners": "PCPHI implements interventions alongside government agencies, bilateral organisations and civil society organisations.",
    "reach": "Its work focuses particularly on hard-to-reach communities, underserved populations and vulnerable groups.",
    "phones": [("+234 903 933 1974", "2349039331974"), ("+234 707 706 6330", "2347077066330")],
    "hero_alt": "Children and staff at a PCPHI Children's Day community impact programme",
    "address": "7 State Specialist Hospital Administrative Building, Ondo City, Ondo State, Nigeria",
    "email": "participativecare@gmail.com", "website": "https://www.participativecare.org.ng",
}
GOALS = [
    ("Promote Preventive Healthcare", "Strengthen community awareness and adoption of preventive health practices to reduce disease burden.", "shield"),
    ("Improve Equitable Healthcare Access", "Expand access to quality, affordable and inclusive healthcare services, particularly for underserved populations.", "compass"),
    ("Strengthen Community Participation", "Empower individuals, families and communities to actively participate in health planning, decision-making and service delivery.", "users"),
    ("Advance Health Literacy", "Improve public knowledge and understanding of health issues through education, sensitisation and evidence-based information.", "book"),
    ("Reduce Public Health Inequalities", "Address barriers, stigma and discrimination affecting vulnerable and marginalised populations.", "scale"),
    ("Strengthen Health Systems and Sustainability", "Promote health systems accountability, community-led advocacy, partnerships and sustainable interventions that improve health outcomes.", "layers"),
]
THEMES = [
    ("Women empowerment and development", "Supporting women to take part in, and benefit from, community health and development work.", "flower"),
    ("Preventive healthcare services", "Screening and preventive services that help communities reduce disease burden.", "shield"),
    ("Maternal health and reproductive counselling services", "Maternal health support and reproductive counselling for women and families.", "heart"),
    ("Public health intervention programmes", "Community-based interventions delivered alongside government and civil society partners.", "pulse"),
    ("Community engagement and health education", "Sensitisation and education that put accurate health information in people's hands.", "users"),
    ("Adolescent health and youth healthcare", "Health information and care that meet the needs of adolescents and young people.", "sprout"),
    ("GHR advocacy and sensitisation", "Advocacy and sensitisation work on GHR.", "megaphone"),
    ("Child welfare and protection", "Promoting the welfare and protection of children in the communities we serve.", "child"),
    ("Research and survey activities", "Research and surveys that generate evidence to guide public health action.", "search"),
]
VALUES = [("Participation", "Communities help plan, decide and deliver."), ("Inclusion", "No community is too hard to reach."),
          ("Equity", "Fair access to quality healthcare."), ("Collaboration", "Working with government, bilateral and civil society partners."),
          ("Education", "Evidence-based information people can use."), ("Sustainability", "Interventions that last beyond a single project.")]
PATHWAYS = {
    "volunteer": ("Volunteer with PCPHI", "Give your time and skills to community health activities.", "heart"),
    "partner": ("Become a strategic partner", "Institutions and organisations: let us explore how we can work together.", "link"),
    "support": ("Support community interventions", "Help sustain interventions that reach underserved communities.", "users"),
    "collaborate": ("Collaborate on public health programmes", "Researchers, practitioners and agencies: co-design and deliver programmes.", "pulse"),
}
INTERESTS = ["Public health updates", "Community programmes", "Volunteer opportunities", "Partnerships and collaboration", "Research and publications", "Events and announcements"]
CATEGORIES = ["Public health articles", "Community sensitisation", "Intervention reports", "Organisational announcements", "Event updates", "Research and survey publications"]
SOCIAL = [("Facebook", "https://www.facebook.com/participativecare"), ("YouTube", "https://www.youtube.com/@participativecare"),
          ("X", "https://x.com/participativecare"), ("LinkedIn", "https://www.linkedin.com/company/participativecare")]
STATUSES = ["Upcoming", "Ongoing", "Completed"]
IMPACT = []  # add verified figures later, e.g. [("1,200", "people reached in 2025")] — nothing is shown until you do
NAV = [("About", [("About PCPHI", "public.about"), ("Our goals", "public.goals"), ("Thematic areas", "public.themes"), ("Governance", "public.governance")]),
       ("Programmes", "public.programmes"), ("Resources", "public.resources"), ("Get involved", "public.get_involved"), ("Contact", "public.contact")]

ICONS = {
    "shield": '<path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z"/><path d="M9 12l2 2 4-4"/>',
    "compass": '<circle cx="12" cy="12" r="9"/><path d="M15.5 8.5l-2 5-5 2 2-5z"/>',
    "users": '<circle cx="9" cy="8" r="3"/><path d="M3 20c0-3.3 2.7-6 6-6s6 2.7 6 6"/><circle cx="17" cy="9" r="2.5"/><path d="M17 14.5c2.5 0 4 1.8 4 4.5"/>',
    "book": '<path d="M4 5c3-1 6-1 8 1 2-2 5-2 8-1v14c-3-1-6-1-8 1-2-2-5-2-8-1z"/><path d="M12 6v14"/>',
    "scale": '<path d="M12 4v16M6 20h12M5 7h14"/><path d="M5 7l-3 7a3 3 0 006 0zM19 7l-3 7a3 3 0 006 0z"/>',
    "layers": '<path d="M12 3l9 5-9 5-9-5z"/><path d="M3 13l9 5 9-5"/>',
    "flower": '<circle cx="12" cy="9" r="5"/><path d="M12 14v8M9 18h6"/>',
    "heart": '<path d="M12 20s-8-5-8-11a4.5 4.5 0 018-2.5A4.5 4.5 0 0120 9c0 6-8 11-8 11z"/>',
    "pulse": '<path d="M3 12h4l2-6 4 12 2-6h6"/>',
    "sprout": '<path d="M12 21v-9"/><path d="M12 12c0-4-3-6-7-6 0 4 3 6 7 6zM12 14c0-3 2.5-5 6-5 0 3-2.5 5-6 5z"/>',
    "megaphone": '<path d="M4 10v4h3l7 4V6L7 10z"/><path d="M18 9c1.5 1 1.5 5 0 6"/>',
    "child": '<circle cx="12" cy="7" r="3"/><path d="M5 21c0-4 3-7 7-7s7 3 7 7z"/>',
    "search": '<circle cx="11" cy="11" r="7"/><path d="M20 20l-4-4"/>',
    "link": '<path d="M10 14a4 4 0 005.7 0l3-3a4 4 0 00-5.7-5.7l-1 1"/><path d="M14 10a4 4 0 00-5.7 0l-3 3a4 4 0 005.7 5.7l1-1"/>',
    "phone": '<path d="M5 4h4l2 5-2.5 1.5a11 11 0 005 5L15 13l5 2v4a2 2 0 01-2 2A16 16 0 013 6a2 2 0 012-2z"/>',
    "chat": '<path d="M4 5h16v11H9l-5 4z"/>', "mail": '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 7l9 6 9-6"/>',
    "pin": '<path d="M12 21s7-6 7-12a7 7 0 10-14 0c0 6 7 12 7 12z"/><circle cx="12" cy="9" r="2.5"/>',
    "menu": '<path d="M4 7h16M4 12h16M4 17h16"/>', "close": '<path d="M6 6l12 12M18 6L6 18"/>',
    "down": '<path d="M6 9l6 6 6-6"/>', "check": '<path d="M5 12l5 5 9-10"/>', "calendar": '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4"/>',
}
