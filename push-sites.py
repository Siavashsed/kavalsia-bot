#!/usr/bin/env python3
"""
push-sites.py  -  Kavalsia Network
Generates unique HTML designs for all 22 GitHub Pages sites.

Usage:
  python push-sites.py --save           # Write to ./site-templates/
  python push-sites.py --push TOKEN     # Push all to GitHub
  python push-sites.py --push TOKEN --only cryptopulse
"""
import base64, json, sys, time, argparse
import requests
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import layout_shell

BASE = Path(__file__).parent
OUT  = BASE / "site-templates"

# ── 22 site configs ────────────────────────────────────────────────────────────
SITES = [
  {
    "repo":"Siavashsed/cryptopulse","id":"cryptopulse","tpl":"terminal",
    "name":"CryptoPulse","tagline":"Algorithmic Trading Intelligence",
    "category":"Crypto & Trading",
    "author":"Siavash Sadighi","author_title":"Crypto Analyst & Algorithmic Trading Strategist",
    "bio1":"I spent eight years running automated crypto strategies at a prop desk in Vancouver before going independent. The edge I found wasn't in being smarter - it was in being more systematic.",
    "bio2":"This site is where I publish the analysis that takes longer than 280 characters to explain: on-chain signals, bot logic, and the setups I'm actually watching.",
    "hero_sub":"On-chain data, systematic signals, and algo trade breakdowns for serious crypto traders.",
    "nl_head":"The Weekly Alpha Report","nl_sub":"Systematic signals, on-chain data, and trade setups - no filler, no hype.",
    "footer_desc":"Evidence-based analysis for algorithmic traders and crypto researchers.",
    "bg":"#050908","bg2":"#081009","surface":"#0c1710",
    "primary":"#00e676","primary2":"#00b85a","text":"#d8f0e0","muted":"#5a8468","brd":"#122216",
    "font_head":"system-ui,sans-serif","font_body":"system-ui,sans-serif","font_mono":"'Courier New',Courier,monospace",
  },
  {
    "repo":"Siavashsed/tradingtechreview","id":"tradingtechreview","tpl":"pulse",
    "name":"TradingTech Review","tagline":"Tools, Code & Platforms for Algo Traders",
    "category":"Trading Technology",
    "author":"Siavash Sadighi","author_title":"Software Engineer & Algorithmic Trading Developer",
    "bio1":"I started as a software engineer writing data pipelines, then spent three years building and running my own algo strategies. I've used, broken, and benchmarked most of the tools in this space.",
    "bio2":"TradingTech Review is where I cut through vendor marketing. If a tool doesn't hold up under real trading conditions, I'll say so.",
    "hero_sub":"Honest reviews of trading platforms, APIs, and code libraries from someone who builds with them.",
    "nl_head":"The Dev Trader Newsletter","nl_sub":"Tool reviews, code snippets, and platform updates worth knowing about.",
    "footer_desc":"Honest tool reviews for developers who trade algorithmically.",
    "bg":"#0d1117","bg2":"#161b22","surface":"#1c2128",
    "primary":"#58a6ff","primary2":"#1f6feb","text":"#e6edf3","muted":"#8b949e","brd":"#21262d",
    "font_head":"system-ui,sans-serif","font_body":"system-ui,sans-serif","font_mono":"'Courier New',Courier,monospace",
  },
  {
    "repo":"Siavashsed/carverge","id":"carverge","tpl":"pulse",
    "name":"CarVerge","tagline":"EV & Automotive Engineering Explained",
    "category":"EV & Automotive",
    "author":"James Carr","author_title":"Automotive Engineer & EV Researcher",
    "bio1":"Fifteen years designing powertrains at an OEM gave me a very specific allergy: I can't stand automotive journalism that doesn't understand how cars actually work.",
    "bio2":"CarVerge exists because most EV coverage is either hype or FUD. I try to give you the engineering reality - battery chemistry, real-world range data, and cost of ownership math.",
    "hero_sub":"Engineering-level EV and automotive analysis. No hype, no brand loyalty - just the technical reality.",
    "nl_head":"CarVerge Dispatch","nl_sub":"EV range data, battery tech, and automotive engineering news - monthly, no spam.",
    "footer_desc":"Technical automotive analysis for engineers, enthusiasts, and informed buyers.",
    "bg":"#040d1a","bg2":"#071428","surface":"#0b1d36",
    "primary":"#60a5fa","primary2":"#2563eb","text":"#e0eeff","muted":"#6494c8","brd":"#0e2040",
    "font_head":"system-ui,sans-serif","font_body":"system-ui,sans-serif","font_mono":"'Courier New',Courier,monospace",
  },
  {
    "repo":"Siavashsed/aimarketingpro","id":"aimarketingpro","tpl":"neon",
    "name":"AI Marketing Pro","tagline":"AI-Powered Marketing That Moves Numbers",
    "category":"AI Marketing",
    "author":"Siavash Sadighi","author_title":"AI Marketing Strategist & Performance Director",
    "bio1":"I've run over $12 million in paid ad spend and managed content ops for B2B and DTC brands. When AI tools started showing up in my workflow, I tested them seriously - not just played with demos.",
    "bio2":"AI Marketing Pro is the resource I wished existed when I started integrating AI into my campaigns. No hype about 'replacing marketers' - just what works, measured by actual results.",
    "hero_sub":"What AI tools actually do for marketing performance - tested with real ad spend and measured results.",
    "nl_head":"The AI Marketing Brief","nl_sub":"What's working in AI marketing this week. Practical, tested, no fluff.",
    "footer_desc":"Real-world AI marketing analysis from a performance background.",
    "bg":"#08060f","bg2":"#100c1a","surface":"#17122a",
    "primary":"#a855f7","primary2":"#7c3aed","text":"#f0e8ff","muted":"#9575cd","brd":"#2a1f45",
    "font_head":"system-ui,sans-serif","font_body":"system-ui,sans-serif","font_mono":"monospace",
  },
  {
    "repo":"Siavashsed/onlinebizpro","id":"onlinebizpro","tpl":"stack",
    "name":"Online Biz Pro","tagline":"Build Something That Runs Without You",
    "category":"Online Business",
    "author":"Siavash Sadighi","author_title":"Serial Entrepreneur & Online Business Advisor",
    "bio1":"I've built and sold three online businesses in the last eight years - a content site, a SaaS tool, and a productized service. None of them required VC money or a big team.",
    "bio2":"Online Biz Pro is for founders who want straight talk on what actually works: acquisition, pricing, hiring, exits. Skip the guru content - this is operating experience.",
    "hero_sub":"Straight talk on building, scaling, and selling online businesses. From someone who has done it multiple times.",
    "nl_head":"The Operator's Weekly","nl_sub":"What's working in online business this week - no guru content, just operator experience.",
    "footer_desc":"Practical online business advice from a founder who has built and sold multiple companies.",
    "bg":"#0a0a0a","bg2":"#141414","surface":"#1c1c1c",
    "primary":"#f59e0b","primary2":"#d97706","text":"#f5f0e8","muted":"#9c8c70","brd":"#2a2520",
    "font_head":"system-ui,sans-serif","font_body":"system-ui,sans-serif","font_mono":"monospace",
  },
  {
    "repo":"Siavashsed/sportiqpro","id":"sportiqpro","tpl":"sportiqpro",
    "name":"SportIQ Pro","tagline":"Performance Science for Serious Athletes",
    "category":"Sports Performance",
    "author":"Coach Daniel Webb","author_title":"CSCS-Certified Strength & Conditioning Coach",
    "bio1":"I've spent 14 years coaching strength and conditioning - from high school varsity teams to professional athletes. The gap between what coaches do and what the research shows is often embarrassingly wide.",
    "bio2":"SportIQ Pro is my attempt to close that gap. Every programming decision, every recovery protocol, every piece of nutrition advice gets run against the actual evidence. No bro science.",
    "hero_sub":"Evidence-based strength and conditioning for athletes who train seriously and want real results.",
    "nl_head":"The Performance Brief","nl_sub":"Weekly programming insights, research breakdowns, and coaching notes.",
    "footer_desc":"Science-based performance coaching for competitive athletes and serious trainers.",
    "bg":"#0f0f12","bg2":"#18181c","surface":"#22222a",
    "primary":"#ef4444","primary2":"#b91c1c","text":"#f8f4f4","muted":"#9c8888","brd":"#2e2222",
    "font_head":"system-ui,sans-serif","font_body":"system-ui,sans-serif","font_mono":"monospace",
  },
  {
    "repo":"Siavashsed/datingedge","id":"datingedge","tpl":"datingedge",
    "name":"The Dating Edge","tagline":"Attachment Psychology for Modern Relationships",
    "category":"Dating & Relationships",
    "author":"Dr. Priya Sharma","author_title":"Clinical Psychologist, Relationships Specialist",
    "bio1":"After a decade in clinical practice working with couples and individuals, I got tired of watching people repeat the same patterns while reading the same surface-level dating advice.",
    "bio2":"The Dating Edge is built around attachment theory, communication research, and the psychology of attraction - not pickup tactics or generic 'love yourself first' platitudes.",
    "hero_sub":"Psychology-based relationship advice for people who want to understand why patterns repeat - and how to change them.",
    "nl_head":"The Relationship Brief","nl_sub":"Weekly insights on attachment, communication, and modern dating psychology.",
    "footer_desc":"Clinical psychology applied to modern dating and relationships.",
    "bg":"#0c0810","bg2":"#160c1c","surface":"#1e1026",
    "primary":"#f43f5e","primary2":"#be123c","text":"#fce8ef","muted":"#a0748a","brd":"#2e1a26",
    "font_head":"system-ui,sans-serif","font_body":"system-ui,sans-serif","font_mono":"monospace",
  },
  {
    "repo":"Siavashsed/fitpulsepro","id":"fitpulsepro","tpl":"bloom",
    "name":"FitPulse Pro","tagline":"Training Science Without the Nonsense",
    "category":"Fitness & Training",
    "author":"Coach Marcus Webb","author_title":"NASM-Certified Personal Trainer",
    "bio1":"Twelve years on the gym floor teaching real people to train. I've heard every excuse, tried every trend, and tracked enough client results to know what actually drives fat loss and muscle gain.",
    "bio2":"FitPulse Pro is for people who want honest answers: what the research says, what my experience confirms, and what the fitness industry is quietly wrong about.",
    "hero_sub":"Training science that holds up in the real world - backed by research, confirmed by 12 years of coaching results.",
    "nl_head":"The Training Signal","nl_sub":"Weekly training insights, protocol breakdowns, and research you can actually use.",
    "footer_desc":"Evidence-based fitness coaching and training science.",
    "bg":"#0c0e14","bg2":"#13161e","surface":"#1a1e28",
    "primary":"#d6ff3f","primary2":"#b8e02a","text":"#f0f1f4","muted":"#9aa0aa","brd":"rgba(255,255,255,.08)",
    "font_head":"'Inter Tight','Inter',system-ui,sans-serif","font_body":"'Inter',system-ui,sans-serif","font_mono":"'JetBrains Mono',ui-monospace,monospace",
    "performance_archive":True,
  },
  {
    "repo":"Siavashsed/supplementverge","id":"supplementverge","tpl":"stack",
    "name":"Supplement Verge","tagline":"What the Research Actually Says",
    "category":"Supplement Science",
    "author":"Dr. James Holloway","author_title":"Sports Scientist & Registered Nutritionist",
    "bio1":"I've spent 11 years reviewing clinical trials and working with competitive athletes on evidence-based nutrition protocols. The gap between what supplement brands claim and what studies show is enormous.",
    "bio2":"Supplement Verge cuts through the marketing. Every ingredient gets graded by the quality of human evidence behind it - not by how impressive the label looks.",
    "hero_sub":"Supplement reviews and nutrition science graded by human clinical evidence. No marketing claims, no sponsored opinions.",
    "nl_head":"The Evidence Brief","nl_sub":"Monthly supplement science roundup - what the trials actually showed.",
    "footer_desc":"Supplement reviews graded by clinical evidence quality.",
    "bg":"#060a07","bg2":"#0c1009","surface":"#121810",
    "primary":"#84cc16","primary2":"#65a30d","text":"#eef8e0","muted":"#7a9860","brd":"#1a2814",
    "font_head":"system-ui,sans-serif","font_body":"system-ui,sans-serif","font_mono":"monospace",
    "stack_topics":["Protein","Creatine","Pre-Workout","Fat Loss","Recovery","Sleep","Testosterone","Evidence Grades"],
  },
  {
    "repo":"Siavashsed/ecommerceedge","id":"ecommerceedge","tpl":"grid",
    "name":"Ecommerce Edge","tagline":"Conversion Strategy for DTC Brands",
    "category":"Ecommerce Strategy",
    "author":"Siavash Sadighi","author_title":"Ecommerce Strategist & DTC Growth Specialist",
    "bio1":"I've consulted on over 50 Shopify stores and helped several DTC brands scale from six figures to eight. Most conversion problems come down to the same five or six mistakes - I've catalogued them all.",
    "bio2":"Ecommerce Edge is where I share the tactics, data, and frameworks that actually move conversion rates. No vanity metrics, no generic advice.",
    "hero_sub":"Proven conversion tactics and DTC strategy from a consultant who has worked with 50+ Shopify stores.",
    "nl_head":"The Conversion Weekly","nl_sub":"One tested ecommerce tactic, every week. Straight to the point.",
    "footer_desc":"Ecommerce conversion strategy and DTC brand consulting insights.",
    "bg":"#ffffff","bg2":"#f8f8f8","surface":"#f0f0f0",
    "primary":"#f97316","primary2":"#ea580c","text":"#111111","muted":"#666666","brd":"#e5e5e5",
    "font_head":"system-ui,sans-serif","font_body":"system-ui,sans-serif","font_mono":"monospace",
  },
  {
    "repo":"Siavashsed/insightinsure","id":"insightinsure","tpl":"slate",
    "name":"Insight Insure","tagline":"Insurance Advice in Plain Language",
    "category":"Insurance",
    "author":"Patrick Lane","author_title":"Independent Insurance Broker & Consumer Advocate",
    "bio1":"I've been an independent insurance broker for 18 years. I work with no single carrier, which means I have zero reason to steer you toward an overpriced policy. That independence is what makes this site possible.",
    "bio2":"Insight Insure exists because insurance is one of the most important financial products most people understand the least. I'm trying to fix that, one article at a time.",
    "hero_sub":"Insurance explained honestly - coverage comparisons, fine print decoded, and the policies you actually need.",
    "nl_head":"The Insure Brief","nl_sub":"Monthly insurance updates and coverage advice in plain English.",
    "footer_desc":"Independent insurance guidance from a broker with no carrier allegiances.",
    "bg":"#f8fafc","bg2":"#f1f5f9","surface":"#e8eef4",
    "primary":"#0891b2","primary2":"#0e7490","text":"#0f172a","muted":"#64748b","brd":"#cbd5e1",
    "font_head":"system-ui,sans-serif","font_body":"system-ui,sans-serif","font_mono":"monospace",
  },
  {
    "repo":"Siavashsed/sellit-ca","id":"sellit-ca","tpl":"grid",
    "name":"Sellit","tagline":"The Unseen Tricks for Selling Your House Better",
    "category":"Home Selling & Real Estate Intel",
    "author":"The Sellit Desk","author_title":"Real Estate Insiders & Everyday Sellers",
    "bio1":"We are a small group of working agents, listing photographers, mortgage brokers, and recent FSBO sellers who got tired of how little useful intel HouseSigma and Realtor.ca actually give a seller. Every piece here was used to sell a real house.",
    "bio2":"Sellit is the layer between the listing portal and the kitchen-table conversation. The tactics, the numbers, the negotiating moves - the things the agent does not write down because nobody is paying them to teach it.",
    "hero_sub":"The tactics agents do not share, the listing tricks portals do not show, and the pricing psychology that decides whether you walk away with the right number. A better, freer version of HouseSigma and Realtor.ca.",
    "nl_head":"The Seller Brief","nl_sub":"One tactical seller move every week. Pricing, staging, negotiating - the moves agents keep off the listing page.",
    "footer_desc":"The unseen tricks for selling your house better. The newest way of house selling, written by everyday people who actually do it.",
    # Dark premium scheme - matches the SHELL navy and fixes the white-on-white
    # contrast bug that made archive card titles invisible.
    "bg":"#0c1018","bg2":"#141a26","surface":"#1a2233",
    "primary":"#c8a96a","primary2":"#9e8654","text":"#f4f6fa","muted":"#9ca5b4","brd":"#27303f",
    "font_head":"'Inter Tight','Inter',system-ui,sans-serif","font_body":"'Inter',system-ui,sans-serif","font_mono":"'JetBrains Mono',ui-monospace,monospace",
    "editorial_archive":True,
    "schema_article_type":"BlogPosting",
  },
  {
    "repo":"Siavashsed/newborniq","id":"newborniq","tpl":"bloom",
    "name":"Newborn IQ","tagline":"Evidence-Based Newborn & Baby Care",
    "category":"Newborn & Baby Care",
    "author":"Melissa Torres","author_title":"NICU Nurse & Mother of Three",
    "bio1":"Twelve years in the NICU watching parents navigate the most overwhelming weeks of their lives taught me one thing: most baby advice is either fear-based or outdated. New parents deserve better.",
    "bio2":"Newborn IQ is built around what current pediatric evidence actually supports - not what worked for someone's grandmother, and not the anxiety-producing content that fills most parenting sites.",
    "hero_sub":"Newborn care advice grounded in current pediatric research - calm, practical, and free of the fear-mongering.",
    "nl_head":"The Parent Brief","nl_sub":"Monthly newborn and baby care updates from a NICU nurse perspective.",
    "footer_desc":"Evidence-based newborn care guidance from a NICU nursing background.",
    "bg":"#f0f9ff","bg2":"#e6f4ff","surface":"#dbeafe",
    "primary":"#0369a1","primary2":"#0284c7","text":"#0c1a2e","muted":"#5b8aad","brd":"#bfdbfe",
    "font_head":"system-ui,sans-serif","font_body":"system-ui,sans-serif","font_mono":"monospace",
  },
  {
    "repo":"Siavashsed/passivewealthguide","id":"passivewealthguide","tpl":"leaf",
    "name":"Passive Wealth Guide","tagline":"Building Income While You Sleep",
    "category":"Passive Income & Investing",
    "author":"Siavash Sadighi","author_title":"Investor & Financial Independence Strategist",
    "bio1":"I retired at 41 by building passive income streams over 15 years - dividend portfolios, REITs, a small rental, and eventually a digital product. None of it happened fast, and that's kind of the point.",
    "bio2":"Passive Wealth Guide is written for people who want the realistic version: how long it actually takes, what the taxes look like, and which strategies are worth the complexity.",
    "hero_sub":"Realistic passive income strategies from a CFP who retired early building them. The math, the timeline, the real results.",
    "nl_head":"The Wealth Letter","nl_sub":"Monthly passive income strategies and investing insights from a CFP who has lived it.",
    "footer_desc":"Realistic passive income guidance from a certified financial planner.",
    "bg":"#faf8f2","bg2":"#f3f0e8","surface":"#ece8dc",
    "primary":"#1a4731","primary2":"#15803d","text":"#1c1a14","muted":"#7a7060","brd":"#d8d0bc",
    "font_head":"Georgia,serif","font_body":"system-ui,sans-serif","font_mono":"monospace",
  },
  {
    "repo":"Siavashsed/mochapoo-pets","id":"mochapoo-pets","tpl":"leaf",
    "name":"MochaPoo Pets","tagline":"The Doodle Breed Expert",
    "category":"Pet Care & Dog Breeds",
    "author":"Dr. Emily Ross","author_title":"Veterinarian & Dog Nutrition Specialist",
    "bio1":"I've been practicing veterinary medicine for 14 years, and doodle mixes have become my most common patients. Mochapoos specifically fascinate me - they've got the intelligence of poodles and the heart of mocha terriers.",
    "bio2":"This site exists because most doodle breed content is written by breeders with a financial stake. I write it as a vet: what the health research shows, what nutrition actually matters, and what advice to ignore.",
    "hero_sub":"Science-backed care guides for Mochapoos and doodle mixes - from a vet who treats them every day.",
    "nl_head":"The Doodle Digest","nl_sub":"Monthly pet care science and breed-specific advice for doodle owners.",
    "footer_desc":"Veterinary guidance for Mochapoo and doodle breed owners.",
    "bg":"#fdf6e3","bg2":"#f8eedb","surface":"#f0e4cc",
    "primary":"#b45309","primary2":"#92400e","text":"#1c1408","muted":"#947040","brd":"#e0cc9a",
    "font_head":"Georgia,serif","font_body":"system-ui,sans-serif","font_mono":"monospace",
    "leaf_stats":[("14","Yrs in Practice"),("DVM","Veterinarian"),("Doodle","Specialist")],
    "leaf_pillars":["Breed Guides","Training Tips","Health & Nutrition","Grooming","Puppy Care"],
    "leaf_vp":[("Vet-Backed Breed Advice","Every care guide is based on peer-reviewed research and clinical experience - not breeder marketing."),("Doodle-Specific Nutrition","Breed-appropriate diet and supplementation guidance based on the unique needs of doodle mixes."),("Real Veterinary Insight","Written by a practicing DVM who sees these dogs daily - what the research shows and what to actually watch for."),("Behavioral Understanding","Why doodles act the way they do - and evidence-backed training that respects how they learn."),("Health Screening","The genetic conditions common in doodle breeds, what to test for, and what questions to ask your vet."),("Owner-Tested Tips","Real advice from thousands of doodle owner interactions - not generic pet care copy.")],
    "leaf_journey":[("Started Practice","Opened a mixed-breed veterinary practice. Doodle mixes became my most frequent patients."),("Noticed the Gap","Most doodle content was written by breeders with a financial stake. The medical accuracy was poor."),("Started Researching","Began compiling breed-specific health research and comparing it to what was being published online."),("Launched the Site","Started MochaPoo Pets to provide veterinary-grade breed information without the breeder bias."),("Today","Still practicing full-time and still writing. Every article is reviewed against current research.")],
    "leaf_approach":[("Start with the science","Breed care recommendations should be grounded in veterinary research, not tradition or marketing."),("Breed-specific beats generic","A Mochapoo has different needs than a Labrador. Generic advice often misses what actually matters."),("Watch for red flags","Know the health markers and behavioral signs that indicate something is off - and what to do about them."),("Ask better questions","Most owners ask the wrong things at vet appointments. Learn the questions that surface real information."),("Build the routine early","Habits set in puppyhood compound over a dog's lifetime. Get the foundations right from the start.")],
  },
  {
    "repo":"Siavashsed/sightreadingacademy","id":"sightreadingacademy","tpl":"leaf",
    "name":"Sight Reading Academy","tagline":"Build Real Musical Fluency",
    "category":"Music Education",
    "author":"Professor Laura Kim","author_title":"Juilliard-Trained Pianist & Music Educator",
    "bio1":"Twenty years of teaching piano at the conservatory level, plus a concert performance career that required reading hundreds of new scores under pressure, gave me a very specific perspective on sight-reading.",
    "bio2":"Most students practice sight-reading wrong - they reinforce bad habits instead of building fluency. Sight Reading Academy is my attempt to fix that with structured, evidence-informed methodology.",
    "hero_sub":"Systematic sight-reading instruction from a Juilliard-trained concert pianist. Build real fluency, not just familiarity.",
    "nl_head":"The Music Letter","nl_sub":"Monthly practice insights and sight-reading methodology for serious students.",
    "footer_desc":"Evidence-based sight-reading instruction for piano and keyboard students.",
    "bg":"#08080b","bg2":"#111116","surface":"#1a1a22",
    "primary":"#f5b14d","primary2":"#e09a31","text":"#eef0f3","muted":"#9aa0a8","brd":"#232328",
    "font_head":"'Cormorant Garamond',Georgia,serif","font_body":"'Inter',system-ui,sans-serif","font_mono":"monospace",
    "leaf_stats":[("20","Yrs Teaching"),("Juilliard","Trained"),("Concert","Performer")],
    "leaf_pillars":["Rhythm Training","Key Signatures","Score Reading","Practice Systems","Music Theory"],
    "leaf_vp":[("Evidence-Based Methodology","Sight-reading fluency is built through specific practice structures - not just repetition. Learn what the research actually says."),("Conservatory-Level Technique","Methods developed through 20 years of teaching at the conservatory level and refined through performance under real pressure."),("Progressive Structured Curriculum","From basic pattern recognition to advanced score reading - a complete system that scales with your level."),("Pattern Recognition Training","Fluency comes from building a library of musical patterns. Learn to see familiar shapes, not decode note by note."),("Performance Pressure Skills","Techniques for maintaining fluency under audition and performance conditions - not just slow practice rooms."),("Independent Practice Design","How to structure your own practice sessions for maximum fluency gain per hour spent.")],
    "leaf_journey":[("Age 5","Started piano lessons. By twelve, decided to pursue it seriously."),("Conservatory","Trained at conservatory level, then graduate study at Juilliard."),("15 Yrs Performing","Concert performance career across three continents requiring constant score reading."),("Transitioned to Teaching","Began conservatory teaching. Identified consistent patterns in how students practiced sight-reading wrong."),("Launched the Academy","Built a structured, research-backed methodology. Sight Reading Academy is that system, available to everyone.")],
    "leaf_approach":[("Read at performance speed","Fluency is built at tempo, not slow practice. Slow reading reinforces hesitation - not skill."),("Use unfamiliar material","Familiarity masks weakness. Use new material constantly so you are reading, not remembering."),("Build pattern recognition","See chord shapes, interval patterns, and rhythmic figures as units - not individual notes."),("Practice the difficult moments","Identify and drill the specific transitions that trip you up, not the sections you already know."),("Track progress systematically","Measure fluency with unfamiliar repertoire at regular intervals. Feeling better is not the same as being better.")],
  },
  {
    "repo":"Siavashsed/dalmend-home","id":"dalmend-home","tpl":"leaf",
    "name":"Dalmend Home","tagline":"Design, Staging & Interior Decisions That Pay Off",
    "category":"Home Design & Real Estate",
    "author":"Olivia Grant","author_title":"Interior Designer & Property Investor",
    "bio1":"I've designed interiors professionally for 11 years while simultaneously flipping six investment properties. That combination taught me what actually adds value versus what just looks good on a mood board.",
    "bio2":"Dalmend Home is where design meets ROI. If a renovation or styling decision doesn't improve livability or resale value, I'll tell you to skip it.",
    "hero_sub":"Interior design advice that considers both aesthetics and financial return - from a designer who also flips properties.",
    "nl_head":"The Home Letter","nl_sub":"Monthly interior design insights and renovation ROI analysis.",
    "footer_desc":"Interior design and home staging advice with a real estate investor's perspective.",
    "bg":"#fefcf7","bg2":"#f7f4ee","surface":"#eeeae0",
    "primary":"#78716c","primary2":"#57534e","text":"#1c1814","muted":"#8c8070","brd":"#ddd8cc",
    "font_head":"Georgia,serif","font_body":"system-ui,sans-serif","font_mono":"monospace",
    "leaf_stats":[("11","Yrs Design"),("6","Properties Flipped"),("ROI","Focused")],
    "leaf_pillars":["Interior Design","Home Staging","Renovation ROI","Color Theory","Property Value"],
    "leaf_vp":[("Design That Earns Back","Every recommendation is filtered through one question: does this add livability or resale value? No mood board fluff."),("Staging That Sells Faster","Proven staging techniques from a designer who has staged and sold six investment properties personally."),("Renovation ROI Analysis","Which upgrades pay off and which are money pits - with real numbers from actual projects, not industry averages."),("Color and Light First","The highest-leverage design decisions involve color and light. Get these right before spending on furniture."),("Furniture That Functions","Pieces chosen for scale, durability, and resale appeal - not just what photographs well."),("Curb Appeal ROI","First impressions drive offers. The exterior decisions that add the most value per dollar spent.")],
    "leaf_journey":[("Started Designing","Began professional interior design work, primarily residential spaces."),("First Investment Property","Bought first flip. Applied design thinking to renovation decisions - focused on what adds value, not just aesthetics."),("Six Properties Later","Six investment properties flipped. Developed a clear sense of which upgrades actually return money."),("Launched Dalmend Home","Started writing about the intersection of design and return on investment. The content that didn't exist."),("Today","Still designing and still investing. Every article is informed by real project numbers.")],
    "leaf_approach":[("ROI filter first","Every design decision passes through one question: does this add livability or resale value?"),("Fix the fundamentals before decorating","Paint, lighting, and layout matter more than furniture. Get those right before spending on accessories."),("Stage to the buyer, not yourself","Staging is not about your taste. It is about helping the specific buyer profile visualize themselves in the space."),("Know your renovation ROI rankings","Kitchen and bathroom updates return. Luxury master suites often do not. Learn which upgrades actually pencil."),("Document everything","Track what you spend and what you sell for. Gut feelings are not data. Real numbers build real judgment.")],
  },
  {
    "repo":"Siavashsed/makeupcraft","id":"makeupcraft","tpl":"bloom",
    "name":"Makeup Craft","tagline":"Professional Technique for Real People",
    "category":"Makeup & Beauty",
    "author":"Sofia Marino","author_title":"Professional MUA & Beauty Educator",
    "bio1":"I've worked as a professional makeup artist for 16 years - fashion weeks, editorial shoots, film sets, and thousands of individual clients. Teaching other artists eventually became as rewarding as the work itself.",
    "bio2":"Makeup Craft is technique-first. I'm not here to sell you a specific product - I'm here to help you understand application, so whatever products you use, you use them correctly.",
    "hero_sub":"Professional makeup technique taught without the product-pushing. Learn application fundamentals that work with any brand.",
    "nl_head":"The Craft Letter","nl_sub":"Monthly technique breakdowns and product notes from a working MUA.",
    "footer_desc":"Professional makeup technique education from a working makeup artist.",
    "bg":"#fffbf9","bg2":"#f8f2ef","surface":"#f0e8e4",
    "primary":"#9f3f55","primary2":"#7f1d3a","text":"#1c1014","muted":"#9c6878","brd":"#e8d0d8",
    "font_head":"Georgia,serif","font_body":"system-ui,sans-serif","font_mono":"monospace",
  },
  {
    "repo":"Siavashsed/travelverge","id":"travelverge","tpl":"atlas",
    "name":"Travel Verge","tagline":"Honest Travel Writing Without the Filters",
    "category":"Travel & Destinations",
    "author":"Ana Verge","author_title":"Independent Travel Journalist",
    "bio1":"I've been traveling and writing independently for nine years, across 63 countries. I've made mistakes most travel bloggers would never admit to - bad border crossings, overpriced accommodation, wrong-season timing.",
    "bio2":"Travel Verge is the resource I wish had existed: specific, honest, and written by someone who went there on their own money. No sponsored stays, no destination board partnerships.",
    "hero_sub":"Independent travel writing built on specific experience - not press trips, not sponsored content, just what actually happened.",
    "nl_head":"The Travel Letter","nl_sub":"Monthly destination guides and travel notes from 60+ countries of independent experience.",
    "footer_desc":"Independent travel writing from a journalist who pays her own way.",
    "bg":"#0d1a1e","bg2":"#132028","surface":"#1a2d38",
    "primary":"#14b8a6","primary2":"#0d9488","text":"#f1f7f5","muted":"#9cbdb5","brd":"#27414d",
    "font_head":"'Merriweather',Georgia,serif","font_body":"'Inter',system-ui,sans-serif","font_mono":"monospace",
  },
  {
    "repo":"Siavashsed/mashestate-construction","id":"mashestate-construction","tpl":"forge",
    "name":"Mash Construction","tagline":"What Your Contractor Won't Tell You",
    "category":"Construction & Renovation",
    "author":"Tom Mash","author_title":"Licensed General Contractor",
    "bio1":"Twenty-two years as a licensed GC and I've watched property owners lose hundreds of thousands to bad bids, unnecessary permits, wrong sequencing, and contractors who took shortcuts they knew the client wouldn't notice.",
    "bio2":"Mash Construction is the resource I give to clients before they start a project. Better-informed owners make better decisions - and my job gets easier when they do.",
    "hero_sub":"Contractor-level renovation knowledge for property owners who want to stop being taken advantage of.",
    "nl_head":"The Build Brief","nl_sub":"Monthly construction advice from a GC who has seen every way a project goes wrong.",
    "footer_desc":"Licensed general contractor insights for property owners and real estate investors.",
    "bg":"#121212","bg2":"#1a1a1a","surface":"#222222",
    "primary":"#ea580c","primary2":"#c2410c","text":"#f5f0e8","muted":"#9c8870","brd":"#2e2820",
    "font_head":"system-ui,sans-serif","font_body":"system-ui,sans-serif","font_mono":"monospace",
  },
  {
    "repo":"Siavashsed/kanona-events","id":"kanona-events","tpl":"kanona",
    "name":"Kanona Projects","tagline":"Experiential Events Designed to Last a Lifetime",
    "category":"Experiential Events & Atmosphere",
    "author":"Kani Sedighi","author_title":"Experiential Event Curator & Creative Director",
    "bio1":"I design events as sensory experiences - where the scent of a room, the weight of silence before music begins, and the specific warmth of candlelight are as deliberate as the guest list. Every detail is a choice.",
    "bio2":"Kanona Projects is for curious minds who believe a gathering can be more than a social obligation. The people who show up wanting to feel something different - and leave carrying a memory they did not expect.",
    "hero_sub":"Sensory design, intimate gatherings, and the architecture of unforgettable evenings. For those who want more from a room.",
    "nl_head":"The Kanona Letter","nl_sub":"One experience a month, described in full. Scent, sound, texture, and what we were thinking when we built it.",
    "footer_desc":"Experiential event curation for curious minds who want more from an evening.",
    "bg":"#080709","bg2":"#0e0c10","surface":"#141218",
    "primary":"#c9a96e","primary2":"#a8883d","text":"#f2ede6","muted":"#8a7a6a","brd":"#2a2430",
    "font_head":"'Cormorant Garamond',Georgia,serif","font_body":"'Inter',system-ui,sans-serif","font_mono":"'JetBrains Mono',ui-monospace,monospace",
    # Opt-in to the editorial luxury /articles archive layout.
    "editorial_archive":True,
  },
  {
    "repo":"Siavashsed/topproduct","id":"topproduct","tpl":"topproduct",
    "name":"TopProduct","tagline":"Editor-Tested Product Picks You Can Actually Trust",
    "category":"Product Reviews & Buying Guides",
    "author":"Sophie Chen","author_title":"Product Editor & Consumer Tech Researcher",
    "bio1":"I test products before writing about them. That sounds obvious but it is not standard practice. Most product content is rewritten spec sheets or affiliate-optimized lists assembled without opening a single box.",
    "bio2":"TopProduct exists because I got tired of buying things based on reviews written by people who had never touched them. Every pick here has been through real use - not a press preview, not a sponsored send.",
    "hero_sub":"Honest product reviews, trending finds, and buying guides. No sponsored fluff - just what is actually worth your money.",
    "nl_head":"The Weekly Pick","nl_sub":"One editor-tested recommendation every Thursday. Products worth buying, and the ones worth skipping.",
    "footer_desc":"Editor-tested product picks, honest buying guides, and trending finds across every category that matters.",
    "bg":"#fafaf8","bg2":"#f2ede6","surface":"#ffffff",
    "primary":"#dc2626","primary2":"#b91c1c","text":"#1a1a17","muted":"#706b60","brd":"#e0dbd2",
    "font_head":"system-ui,sans-serif","font_body":"system-ui,sans-serif","font_mono":"monospace",
  },
  {
    "repo":"Siavashsed/folioatelier","id":"folioatelier","tpl":"editorial",
    "name":"Folio Atelier","tagline":"A curated lens on art, ateliers, and modern collectives.",
    "category":"Arts & Collectives",
    "author":"Imogen Salinger","author_title":"Independent Art Editor",
    "bio1":"I write about artists who haven't figured out a brand yet and ateliers that still smell like turpentine.",
    "bio2":"Folio Atelier is a quiet, curated index for collectors, curators, and the genuinely curious.",
    "hero_sub":"A slow, considered index of artists, ateliers, and small collectives worth knowing.",
    "nl_head":"The Folio Dispatch","nl_sub":"One studio visit and one acquisition note a week, in your inbox.",
    "footer_desc":"A curated lens on art, ateliers, and modern collectives.",
    "bg":"#f6f1ea","bg2":"#ece5da","surface":"#ffffff",
    "primary":"#7b4a32","primary2":"#5e3823","text":"#1a1612","muted":"#6c5d50","brd":"#d8cdbb",
    "font_head":"'Cormorant Garamond',Georgia,serif","font_body":"'Inter',system-ui,sans-serif","font_mono":"'IBM Plex Mono',monospace",
  },
  {
    "repo":"Siavashsed/modeformstudio","id":"modeformstudio","tpl":"editorial",
    "name":"Modeform Studio","tagline":"Where fashion design and modeling are taken seriously.",
    "category":"Fashion Design & Modeling",
    "author":"Lila Vandermeer","author_title":"Fashion Editor & Casting Director",
    "bio1":"Fifteen years on set in Paris, New York, and Antwerp. I cover the studios, agencies, and people who actually move the field.",
    "bio2":"Modeform Studio is for designers, models, casting directors, and the agencies that hire them - written by someone in the room.",
    "hero_sub":"Studios, casting, craft. An insider read on independent fashion design and modeling.",
    "nl_head":"The Modeform Letter","nl_sub":"One studio visit, one casting note, one industry read each week.",
    "footer_desc":"Independent fashion design and modeling, taken seriously.",
    "bg":"#0e0d0c","bg2":"#161412","surface":"#1d1a17",
    "primary":"#e8c47a","primary2":"#c79f57","text":"#f4f0ea","muted":"#8d847a","brd":"#2a2622",
    "font_head":"'Playfair Display',Georgia,serif","font_body":"'Inter',system-ui,sans-serif","font_mono":"'IBM Plex Mono',monospace",
  },
  {
    "repo":"Siavashsed/calibernotes","id":"calibernotes","tpl":"editorial",
    "name":"Caliber Notes","tagline":"Mechanical watches, decoded.",
    "category":"Watches & Horology",
    "author":"Henrik Voss","author_title":"Independent Watchmaker & Critic",
    "bio1":"Twelve years on the bench at a small Swiss restorer. I write about movements the way other people write about engines.",
    "bio2":"Caliber Notes is a technical, no-marketing read on mechanical watches - independents, vintage, complications, and the rare honest movement.",
    "hero_sub":"Movements, references, and the people who make them. Technical notes on mechanical watches.",
    "nl_head":"Service Interval","nl_sub":"One movement breakdown and one buying note each week.",
    "footer_desc":"Technical, independent notes on mechanical watches.",
    "bg":"#111418","bg2":"#181c22","surface":"#20252c",
    "primary":"#cdb87a","primary2":"#a89456","text":"#e8ecf2","muted":"#8b95a3","brd":"#262d36",
    "font_head":"'EB Garamond',Georgia,serif","font_body":"'Inter',system-ui,sans-serif","font_mono":"'JetBrains Mono',monospace",
  },
  {
    "repo":"Siavashsed/crestcharter","id":"crestcharter","tpl":"editorial",
    "name":"Crest Charter","tagline":"Private jets, villas, and yachts - vetted, never marketed.",
    "category":"Luxury Rentals - Jets, Villas, Yachts",
    "author":"Adrien Marchetti","author_title":"Private Travel Director",
    "bio1":"Two decades booking aircraft, charters, and staffed villas for clients who value discretion more than they value chrome.",
    "bio2":"Crest Charter is a vetted, no-affiliate guide to private aviation, superyacht charter, and ultra-luxury villa rentals - written by an operator.",
    "hero_sub":"Private aviation, superyacht charter, and staffed villas - vetted by someone who actually books them.",
    "nl_head":"The Crest Brief","nl_sub":"One destination, one operator note, one insider tip each week.",
    "footer_desc":"Private jets, villas, and yachts - vetted, never marketed.",
    "bg":"#06121a","bg2":"#0c1c27","surface":"#102536",
    "primary":"#c9a55c","primary2":"#a4823f","text":"#eef4f9","muted":"#7d97ac","brd":"#15303f",
    "font_head":"'Cormorant Garamond',Georgia,serif","font_body":"'Inter',system-ui,sans-serif","font_mono":"'IBM Plex Mono',monospace",
  },
  {
    "repo":"Siavashsed/strobeatlas","id":"strobeatlas","tpl":"editorial",
    "name":"Strobe Atlas","tagline":"Raves, halloween, warehouses, and university nights, done properly.",
    "category":"Nightlife & Parties",
    "author":"Riv Solano","author_title":"Party Correspondent",
    "bio1":"Eight years writing from the floor at warehouses, festivals, and student nights across Europe, Latin America, and the UK.",
    "bio2":"Strobe Atlas is a global index of nightlife - field reports, set times, lineups, and the small details that separate a good night from one you will still talk about in five years.",
    "hero_sub":"The global index of nightlife - raves, halloween, warehouses, university nights, and the people who throw them.",
    "nl_head":"The Guest List","nl_sub":"One night, one set, one city worth booking a flight for, every week.",
    "footer_desc":"Raves, halloween, warehouses, and university nights, done properly.",
    "bg":"#050507","bg2":"#0d0d12","surface":"#13131a",
    "primary":"#ff2bd6","primary2":"#c6ff3a","text":"#f4f4f6","muted":"#8a8a96","brd":"#23232c",
    "font_head":"'Space Grotesk','Anton',system-ui,sans-serif","font_body":"'Inter',system-ui,sans-serif","font_mono":"'JetBrains Mono',monospace",
  },
  {
    "repo":"Siavashsed/mindframe","id":"mindframe","tpl":"editorial",
    "name":"MindFrame","tagline":"Psychology + Neurobiology, made useful.",
    "category":"Psychology & Neurobiology",
    "author":"Dr. Maya Holloway","author_title":"Cognitive Neuroscientist + Editor",
    "bio1":"I spent eight years running working-memory and attention experiments at a behavioral neuroscience lab before going independent. The papers were dense - the takeaways were not.",
    "bio2":"MindFrame translates serious psychology and brain research into things you can actually do. Evidence first, no clickbait, no neuro-pop nonsense.",
    "hero_sub":"Self-tests, tools, and evidence-led writing on memory, sleep, attention, emotion, habits, and cognition.",
    "nl_head":"The MindFrame Brief","nl_sub":"One short, evidence-led essay each week. No filler, no fear-mongering.",
    "footer_desc":"Evidence-led psychology and neurobiology for curious adults.",
    "bg":"#0b1224","bg2":"#0f1830","surface":"#fbf8f1",
    "primary":"#ff5a4e","primary2":"#e0463b","text":"#f5f1e8","muted":"#9aa3b8","brd":"#1a2440",
    "font_head":"'Newsreader',Georgia,serif","font_body":"'Inter',system-ui,sans-serif","font_mono":"'JetBrains Mono',monospace",
  },
  {
    "repo":"Siavashsed/agyan","id":"agyan","tpl":"leaf",
    "name":"Agyan","tagline":"An academy of breath, language, and cosmos",
    "category":"Spiritual Practice & Cosmology",
    "author":"Avin Dabaghchimokri","author_title":"Founder, Agyan Academy",
    "bio1":"بنیان‌گذار آکادمی آگیان، معلم تمرین و خوانندهٔ نقشهٔ زایچه. زادهٔ ۲۱ آوریل ۱۹۷۱ در مهاباد. دو زبان مادری: کردی سورانی و فارسی. پنج سال شاگردی نزد شیخی قادری در سنندج، سپس سال‌ها مطالعه در روان‌شناسی عمق و سنت صوفی.",
    "bio2":"آگیان یک نهاد مستقل آموزشی است که در ۱۳۹۳ بنیان گذاشته شد. چهار شاخهٔ کاری: مدیتیشن، تجلی، کیهان‌نگاری و آیین کلام. هر شاخه دوازده درس، با تمرین آرام و روزانه.",
    "hero_sub":"پژوهش و تمرین در نَفَس، تجلی، کیهان‌نگاری و آیین کلام. چهار شاخهٔ کاری. یک سال مطالعهٔ آهسته.",
    "nl_head":"نامهٔ آگیان","nl_sub":"یک نامهٔ ماهانه. یک نیت، یک تمرین، یک ارجاع به کتاب.",
    "footer_desc":"آکادمی آگیان، نهادی مستقل برای پژوهش و تمرین در نَفَس، زبان و کیهان.",
    "bg":"#0d0a13","bg2":"#1a0e1d","surface":"#241a2a",
    "primary":"#e6b9a6","primary2":"#c98a73","text":"#f5e6d3","muted":"#a89aa6","brd":"rgba(245,230,211,.10)",
    "font_head":"'Newsreader',Georgia,serif","font_body":"'Inter',system-ui,sans-serif","font_mono":"'JetBrains Mono',monospace",
    "leaf_stats":[("۲۰۱۴","Founded"),("۴","Tracks"),("۴۸","Lessons")],
    "leaf_pillars":["Meditation","Manifestation","Astrology","Affirmation","Somatic Practice"],
    "leaf_vp":[("Slow study, deliberate","A full year per track. Twelve lessons. No fast certifications, no upsells, no app."),("Lineage, not invention","Rooted in the Qadiri tradition of Kurdistan, in depth psychology, and in the older Ptolemaic astrological vocabulary."),("Practice over theory","Every lesson has a daily exercise. Breath, journal, observation. Reading without sitting is not study."),("Three languages","Persian, English, Sorani Kurdish. The cosmology is older than any single language; the academy refuses to choose one."),("Body before mind","Somatic anchoring precedes contemplative work. The body is not a metaphor; it is where the practice begins."),("No social media","The academy keeps no Instagram or Twitter presence. One monthly letter. One private cohort twice a year.")],
    "leaf_journey":[("Mahabad, early years","Born 1971 in Mahabad, foothills of the Zagros. Two tongues at home: Sorani Kurdish and Persian."),("Sanandaj apprenticeship","Five years with a Qadiri sheikh in Sanandaj. First learned that silence is a technique, not a temperament."),("The reading years","Jung, Hillman, Marie-Louise von Franz. Translated fragments of depth psychology into Persian for friends."),("The Arabic years","Three winters in Damascus and Cairo reading the classical Sufi corpus in its original language."),("California, somatics","Two retreats with Tara Brach. A year at Esalen as a working scholar in somatic experiencing."),("Founding Agyan","Returned to Mahabad in 2014. First cohort of seven students. Twelve lessons on the back of an envelope.")],
    "leaf_approach":[("Sit before you speak","Twenty minutes of silence opens every session. Words come after the body has settled."),("Read in three tongues","Cosmology survives translation poorly. We hold Persian, English, and Sorani Kurdish in parallel."),("Practice daily, write weekly","A short daily exercise. A weekly written reflection. No exception."),("Use the body as evidence","Test every claim against your own breath, sleep, and attention before believing it."),("Refuse the spectacle","No retreats with photographers. No graduation ceremonies. The work is its own reward.")],
  },
  {
    "repo":"Siavashsed/apex","id":"apex","tpl":"leaf",
    "name":"Apex Dental Journal","tagline":"Peer-reviewed dental practice, distilled",
    "category":"Clinical Dentistry Education",
    "author":"Dr. Tofigh Sedighi","author_title":"Editor-in-Chief, Apex Dental Journal",
    "bio1":"سردبیر مجلهٔ دندانپزشکی اپکس، دکتر توفیق صدیقی. زادهٔ ۱۳۴۳ در مهاباد، دانش‌آموختهٔ دندانپزشکی در سال ۱۳۶۵. پنج دهه طبابت بالینی و تدریس. زبان مادری: کردی سورانی. زبان‌های کار: فارسی، انگلیسی، عربی.",
    "bio2":"اپکس، مجله‌ای دندانپزشکی، در پنج محور پسادکتری: پیشگیری و بهداشت، دندانپزشکی کودکان، ترمیمی و زیبایی، اورژانس‌های دندانی، و ارتباطات سیستمیک. هر محور دوازده درس ساخت‌یافته بر پایهٔ شواهد بالینی.",
    "hero_sub":"مجلهٔ دندانپزشکی، بر پایه‌ی پنج دهه طبابت. پنج محور آموزش پسادکتری. یک رشتهٔ علمی: حفاظت از مینای دندان.",
    "nl_head":"نامهٔ اپکس","nl_sub":"یک نامهٔ ماهانه با یک مقالهٔ بازخوانی‌شده و یک یادداشت بالینی.",
    "footer_desc":"مجلهٔ دندانپزشکی اپکس، نشریه‌ای علمی به سردبیری دکتر توفیق صدیقی.",
    "bg":"#fdfcf8","bg2":"#fafaf7","surface":"#ffffff",
    "primary":"#0f6e6c","primary2":"#0a4f4d","text":"#1a1f1e","muted":"#5a6c66","brd":"rgba(15,110,108,.08)",
    "font_head":"'Newsreader',Georgia,serif","font_body":"'Inter',system-ui,sans-serif","font_mono":"'JetBrains Mono',monospace",
    "leaf_stats":[("50+","Yrs Practice"),("5","Tracks"),("FA / EN / CKB","Languages")],
    "leaf_pillars":["Prevention","Pediatric","Restorative","Emergency","Systemic Health"],
    "leaf_vp":[("Evidence-based education","Every lesson and every article is built on the clinical literature. Citations are inline. Statements are testable."),("Five decades of observation","The curriculum is shaped by what actually happens in a working clinic, not by textbook generalities."),("Open-access first three lessons","The first three lessons of each track are free, forever. No paywall, no email gate, no registration to read."),("Three working languages","Persian, English, Sorani Kurdish. Clinical knowledge belongs to the patients who carry their teeth home, in their tongue."),("Conservative bias","When in doubt, do less. Preserve enamel. Preserve pulp. Preserve the patient's own tooth wherever possible."),("Tools, not gimmicks","The lab section is built for actual clinical decisions: brushing technique, fluoride dosing, post-extraction timing.")],
    "leaf_journey":[("1964 Mahabad","Born in Mahabad, West Azerbaijan, in the heart of Kurdistan."),("Dental school","Trained in dentistry, graduated D.D.S. in 1986."),("Early clinical years","First two decades focused on prevention and pediatric work in the underserved north-west."),("University teaching","Twelve years lecturing in restorative dentistry and emergency care."),("Founding Apex","Apex Dental Journal, named for the anatomical tip of the tooth root, was founded as a peer-reviewed venue to distill five decades of clinical observation. Every article is reviewed against the literature before publication."),("Today","Continues part-time clinical work; writes and reviews the journal's published articles personally.")],
    "leaf_approach":[("Cite the literature","Every claim links to a real source: a journal, a guideline, or a peer-reviewed paper. No assertion stands alone."),("Conservative first","Drill less. Preserve more. The healthiest restoration is the one you do not need."),("Teach the technique, not the brand","Brushing pressure, paste quantity, flossing angle. The product matters less than the motion."),("Write for the patient too","Every clinical article includes a plain-language section the patient can read."),("Question your reflexes","After fifty years, the most dangerous habit is certainty. Reconsider familiar diagnoses every season.")],
  },
]


# ── Single source of truth: merge network-config.json into SITES ───────────────
# The hardcoded SITES list above carries the visual/copy fields each site needs
# at build time (palette, fonts, hero copy). network-config.json carries the
# behavior flags edited by the dashboard (active, persona, tone, editorial_archive,
# custom_domain, schema_article_type, posts_per_day_new, etc.).
#
# Historically these two stores drifted - flipping a flag in network-config did
# nothing because push-sites.py never read it. This merge runs at module load so
# any field present in network-config wins for matching site IDs, and any extra
# fields (e.g. editorial_archive, custom_domain, persona) become available on
# the same `s` dict the generators consume.
# ── Kit presets (palette + fonts + layout for each template kit) ──────────────
# Used when a new site is added via the Add-Site wizard. The site's network-
# config entry gets a `kit: "<slug>"` field and this preset fills in any visual
# fields the user didn't override. Keeps the kit choice as the single design
# decision instead of forcing the user to pick a palette by hand.
KIT_PRESETS = {
    "editorial-luxury": {
        "bg":"#080709","bg2":"#0e0c10","surface":"#141218",
        "primary":"#c9a96e","primary2":"#a8883d","text":"#f2ede6","muted":"#9a8d7d","brd":"#2a2430",
        "font_head":"'Cormorant Garamond',Georgia,serif",
        "font_body":"'Inter',system-ui,sans-serif",
        "font_mono":"'JetBrains Mono',ui-monospace,monospace",
        "tpl":"kanona",
        "editorial_archive":True,
        "schema_article_type":"CreativeWork",
    },
    "tech-modern": {
        "bg":"#0a0e1a","bg2":"#10162a","surface":"#1a2238",
        "primary":"#3b82f6","primary2":"#1d4ed8","text":"#f1f5f9","muted":"#94a3b8","brd":"#1e2a4a",
        "font_head":"'Inter',system-ui,sans-serif",
        "font_body":"'Inter',system-ui,sans-serif",
        "font_mono":"'JetBrains Mono',ui-monospace,monospace",
        "tpl":"cryptopulse",
        "schema_article_type":"TechArticle",
    },
    "news-magazine": {
        "bg":"#fdfdfb","bg2":"#f4f1ec","surface":"#ffffff",
        "primary":"#dc2626","primary2":"#991b1b","text":"#0e0d0c","muted":"#5a5852","brd":"#e6e2d8",
        "font_head":"'Playfair Display',Georgia,serif",
        "font_body":"'Inter',system-ui,sans-serif",
        "font_mono":"'JetBrains Mono',ui-monospace,monospace",
        "tpl":"sportiqpro",
        "schema_article_type":"NewsArticle",
    },
    "broadsheet": {
        "bg":"#f4f0e8","bg2":"#ece6da","surface":"#fffaf0",
        "primary":"#1a1812","primary2":"#3a3528","text":"#1a1812","muted":"#5a5448","brd":"#d8d2c4",
        "font_head":"'Libre Caslon Text','Times New Roman',serif",
        "font_body":"'Inter',system-ui,sans-serif",
        "font_mono":"'Courier New',monospace",
        "tpl":"folioatelier",
        "schema_article_type":"ReportageNewsArticle",
    },
    "minimalist": {
        "bg":"#ffffff","bg2":"#f8f8f7","surface":"#ffffff",
        "primary":"#0a0a0a","primary2":"#404040","text":"#0a0a0a","muted":"#737373","brd":"#e5e5e5",
        "font_head":"'Fraunces',Georgia,serif",
        "font_body":"'Inter',system-ui,sans-serif",
        "font_mono":"'JetBrains Mono',ui-monospace,monospace",
        "tpl":"modeformstudio",
        "schema_article_type":"BlogPosting",
    },
}


def _site_dict_from_network_entry(nc_entry):
    """Synthesize a SITES-shaped dict from a network-config entry that has no
    corresponding hardcoded SITES entry. Pulls visual defaults from the kit
    preset named in `kit`, then overlays any explicit network-config fields."""
    kit = (nc_entry.get("kit") or "minimalist").strip().lower()
    preset = dict(KIT_PRESETS.get(kit, KIT_PRESETS["minimalist"]))
    sid = nc_entry.get("id", "")
    site = {
        "repo": nc_entry.get("repo") or f"Siavashsed/{sid}",
        "id": sid,
        "tpl": preset.get("tpl", "minimalist"),
        "name": nc_entry.get("name", sid),
        "tagline": nc_entry.get("tagline", ""),
        "category": nc_entry.get("category", "General"),
        "author": nc_entry.get("default_author") or "Editorial Team",
        "author_title": nc_entry.get("author_title", "Editor"),
        "bio1": (nc_entry.get("author_bio") or "Editor of this site.")[:300],
        "bio2": "",
        "hero_sub": nc_entry.get("hero_sub") or nc_entry.get("tagline") or "",
        "nl_head": "Newsletter",
        "nl_sub": "Get our best work delivered. No spam.",
        "footer_desc": nc_entry.get("footer_desc") or nc_entry.get("tagline") or "",
    }
    # Fill in palette + fonts from kit preset
    for k in ("bg","bg2","surface","primary","primary2","text","muted","brd",
              "font_head","font_body","font_mono"):
        site[k] = preset.get(k, "")
    return site


def _merge_network_config_into_sites():
    try:
        import json as _json
        from pathlib import Path as _Path
        cfg_path = _Path(__file__).parent / "network-config.json"
        if not cfg_path.exists():
            return
        cfg = _json.loads(cfg_path.read_text(encoding="utf-8"))
        by_id = {s.get("id"): s for s in cfg.get("sites", []) if s.get("id")}
        existing_ids = {s.get("id") for s in SITES}
        # Apply overrides to known sites
        for site in SITES:
            sid = site.get("id")
            override = by_id.get(sid)
            if not override:
                continue
            for k, v in override.items():
                if k in {"id", "repo"}:
                    continue
                if k in {"bg", "bg2", "surface", "primary", "primary2",
                         "text", "muted", "brd",
                         "font_head", "font_body", "font_mono",
                         "tagline", "hero_sub", "footer_desc", "nl_head", "nl_sub",
                         "author_title", "tpl"}:
                    if v in (None, "", []):
                        continue
                site[k] = v
        # Append any network-config sites that aren't in the hardcoded list.
        # Lets new sites added via the dashboard appear without editing source.
        for nc_entry in cfg.get("sites", []):
            sid = nc_entry.get("id")
            if not sid or sid in existing_ids or sid == "nexus":
                continue
            if nc_entry.get("is_mother_site"):
                continue
            new_site = _site_dict_from_network_entry(nc_entry)
            # Overlay any direct overrides from network-config on top
            for k, v in nc_entry.items():
                if k in {"id", "repo"} or v in (None, "", []):
                    continue
                new_site[k] = v
            SITES.append(new_site)
    except Exception:
        pass

_merge_network_config_into_sites()


# ── Per-site story content (4-5 paragraphs per author) ─────────────────────────
STORIES = {
  "cryptopulse": [
    "I grew up in a household where money was taken seriously. My parents had immigrated and built everything from nothing, and that shaped how I thought about risk before I ever traded a single position. Not as something to avoid, but as something to size correctly.",
    "My path into trading started through software. I studied mathematics at university and got hired by a small prop trading firm in Vancouver as a data analyst. Within eight months I was running my own book. Within two years I had blown it up, rebuilt it, and finally started making consistent returns.",
    "Crypto entered my world in 2016. I spent about six months watching on-chain data before building my first automated strategy. It lost money for four months before I understood the gap between what I thought I was measuring and what actually drove price. That gap is the real curriculum in this space.",
    "Running automated strategies at a prop desk for eight years gave me perspective on the full lifecycle of a trading idea - conception, backtesting, live deployment, degradation, and retirement. Most edges have a shelf life. The discipline is recognizing when to retire a strategy rather than explaining away its losses.",
    "I went independent three years ago. CryptoPulse is where I publish the longer analysis - on-chain research, strategy breakdowns, and market structure observations that take more than a short post to explain properly. No hype, no calls, no FOMO. Just the systematic work.",
  ],
  "tradingtechreview": [
    "My career started in data engineering, not trading. I spent four years building pipelines and dashboards for a logistics company before a friend introduced me to algorithmic trading as a side project. That side project consumed the next three years of evenings and weekends.",
    "I started running real money with my own strategies while still working full time. The tooling problems hit immediately - data feeds that missed ticks, broker APIs that documented features they had not actually built, backtesting platforms that produced results impossible to replicate live. The gap between what vendors promised and what traders actually experienced was enormous.",
    "By the time I went full time into algo trading, I had tested or integrated with more platforms than I could count. I broke things other traders took for granted. I found edge cases that documentation never mentioned. I became the person other traders asked before committing to a new tool.",
    "TradingTech Review started as a private notes system - a running record of what I had tested, what failed, and what the actual limitations were. The notes got shared around. People found them more honest than any official review or vendor comparison.",
    "The site now covers the full stack: data providers, execution platforms, backtesting frameworks, broker APIs, and the code libraries that connect them. If a tool has a problem I missed initially, I update the review. The goal is the resource I wished had existed when I started.",
  ],
  "carverge": [
    "I spent fifteen years at an automotive OEM designing and testing powertrain systems. In that time I watched the industry move from skepticism about electrification to full commitment to it, with a front-row seat to the technical reality behind the headlines.",
    "My engineering background means I approach EV coverage differently than most automotive journalists. When a manufacturer announces a range figure, I want to know the test cycle, the ambient temperature, the driving speed profile, and the battery chemistry. The headline number is rarely the one that matters.",
    "The transition from internal combustion to electric has genuine engineering advantages and genuine limitations. EV advocates overstate range and understate charging infrastructure gaps. Critics overstate degradation and understate total cost of ownership benefits. The engineering reality is more nuanced than either side admits.",
    "I left the OEM after fifteen years to work as an independent engineering consultant. That independence means I have no reason to favor any manufacturer and no relationships that require protecting. When something is overengineered, underbuilt, or misrepresented, I will say so.",
    "CarVerge exists because the quality of automotive technical analysis available to consumers is poor. Battery chemistry, real-world efficiency data, powertrain architecture, cost of ownership math - these should be accessible to anyone making a significant purchase decision.",
  ],
  "aimarketingpro": [
    "I started in media buying when the best optimization tool was a spreadsheet and a lot of patience. I learned the fundamentals under people who had been doing it since before Facebook had a pixel, and developed a deep appreciation for what measurable actually means in advertising.",
    "Over twelve years I worked up to managing over twelve million dollars in annual ad spend across multiple brands. I have managed performance teams, built internal analytics systems, and consulted for brands from early-stage to enterprise. The craft is the same at any scale - isolate the variable, measure the outcome, repeat.",
    "When AI tools started arriving in marketing workflows, I approached them the way I approach any new tactic: with a test budget, clear success criteria, and patience for actual results. Most of what I tested did not survive contact with real campaign data. Some of it genuinely moved numbers.",
    "Most AI marketing content is written by people who are selling AI tools or by consultants who have not run a campaign in years. The coverage defaults to demos and use cases rather than measured outcomes. I found that frustrating enough to start writing about what I was actually seeing.",
    "AI Marketing Pro is the record of what I have tested, what worked, and what the realistic impact looks like in actual campaign performance. Not demos, not theory - results from real budgets with real attribution attached.",
  ],
  "onlinebizpro": [
    "My first online business was a content site in a niche I genuinely cared about. I spent a year building it in the evenings after work, eventually hit enough traffic to monetize, and sold it four years after launching for a multiple that made the evenings worthwhile. That first exit taught me more about valuation and buyer behavior than anything I had read.",
    "The second business was a SaaS tool. The third was a productized service. Each taught different lessons about revenue quality, churn, customer acquisition cost, and what a potential acquirer actually cares about when they look at your numbers. Not all revenue is equal, and the sooner you understand that, the better your decisions get.",
    "What struck me after building and selling multiple businesses was how consistent the patterns were. The same mistakes showed up at every stage. The same metrics separated businesses that sold well from businesses that sold poorly. The path was learnable, but most people had to learn it through expensive mistakes.",
    "Most online business content is produced by people who have not built or sold a business at any serious scale. It defaults to tactics rather than operating principles. It confuses traffic with revenue, revenue with profit, and profit with a business worth buying.",
    "Online Biz Pro is for operators who want the direct version: how to structure equity, price a service correctly, think about acquisition channels, and eventually exit on favorable terms. Everything published here comes from the experience of actually building and selling, not from theorizing about it.",
  ],
  "sportiqpro": [
    "I played competitive football through college and knew before I graduated that my future was in coaching rather than playing. I got my CSCS certification immediately after my degree and started coaching at a university strength program while completing my graduate work in exercise science.",
    "Fourteen years of coaching athletes across multiple sports and levels has given me a clear picture of the gap between sports science research and actual coaching practice. That gap is often embarrassingly wide. Published research on recovery says one thing, and most programs do the opposite.",
    "My coaching work eventually moved into professional settings. Working with athletes competing for contracts accelerated my education significantly - when the margin for programming errors shrinks to zero, you get clear on what the evidence actually supports versus what you assumed.",
    "What frustrates me most about online fitness content is the confident presentation of ideas that do not hold up to the evidence. Bro science is still everywhere. Recovery protocols are still promoted based on anecdote. Nutrition advice is still dominated by tribal allegiances rather than controlled trials.",
    "SportIQ Pro is my attempt to close the gap between what the research shows and what athletes actually implement. Every article connects a practical recommendation to the evidence behind it. The reasoning is visible so athletes can evaluate it themselves.",
  ],
  "datingedge": [
    "I trained as a clinical psychologist with a specialization in couples and relationship therapy. My doctoral research focused on attachment patterns in adult relationships, and I have spent the past decade in clinical practice working with both individuals and couples navigating relationship difficulties.",
    "After a decade of practice, the patterns become hard to unsee. The same attachment styles produce the same relationship dynamics across thousands of clients. The same communication failures appear across every demographic. The same fears drive behaviors that people genuinely do not understand about themselves.",
    "What always struck me was the disconnect between what my clients needed - a framework for understanding their own patterns - and what the mainstream dating advice industry offered them. Most dating content is tactical at best and counterproductive at worst.",
    "Attachment theory, developed from decades of research on how early relational experiences shape adult bonding behavior, is the framework that consistently makes sense of what I observe in clinical practice. Understanding it changes what you notice about your own reactions and what you look for in a partner.",
    "The Dating Edge is my attempt to bring clinical-level frameworks into a format accessible to people who are not in therapy. The goal is understanding, not just tactics. If you understand why your patterns repeat, you can actually change them.",
  ],
  "fitpulsepro": [
    "I started training seriously in college, not because I was competitive, but because I was frustrated. I was putting in hours and not seeing results, and I needed to understand why. That frustration sent me down a research rabbit hole that eventually became a career.",
    "I got certified and started coaching clients while still finishing my degree. My early clients were mostly regular people with busy lives who wanted to look and feel better - not athletes, not competitors, just people trying to get real results from training. Understanding what works for that population is its own discipline.",
    "Twelve years on the gym floor has given me a clear picture of what actually drives results versus what looks good in a training video. Most people overtrain specific muscles and underload basic movement patterns. Most people track the wrong variables. Most people stop progressing not because they need a new program but because they need to execute the basics better.",
    "The fitness industry has a serious credibility problem. Advice is dominated by people selling products, people with unusual genetics presenting their experience as universally applicable, and people who have never coached a real client outside a controlled environment.",
    "FitPulse Pro is the signal. Every recommendation is grounded in what the research says and confirmed by what I have seen across thousands of client results. No products to sell, no affiliations that bias my recommendations.",
  ],
  "supplementverge": [
    "I studied sports science at university and spent my graduate years in a lab reviewing clinical literature on ergogenic aids. The contrast between what the research showed and what was being marketed to athletes in the supplement aisle was what set me on this path.",
    "After graduate work I started consulting with competitive athletes on evidence-based nutrition. Most of them had been spending significant money on supplements that lacked credible human evidence. A few were taking things that studies actively suggested were ineffective.",
    "Eleven years of working with athletes and reviewing clinical trials gives you a clear hierarchy - the evidence for creatine and caffeine is deep and consistent; the evidence for dozens of popular products is thin or nonexistent; a meaningful number of products have been studied and found to underperform their marketing claims significantly.",
    "Supplement Verge was born from frustration with review content that read like marketing copy or relied on mechanism-based reasoning rather than human outcome data. The fact that something works in a cell culture study does not mean it works at a dose you can consume without side effects in real human physiology.",
    "Every ingredient on this site gets graded by the quality and consistency of human evidence available - how many trials, how many subjects, what outcomes were measured, what the effect size actually was. That is the only honest way to evaluate a supplement.",
  ],
  "ecommerceedge": [
    "I started as a Shopify developer hired to build custom storefronts. Within a year I had seen enough of what happened after launch to know that the build was rarely the problem. The problem was what happened when real traffic met actual product pages and the checkout flow.",
    "I transitioned into ecommerce consulting and spent the next several years auditing conversion paths for brands at every stage - from early DTC launches to eight-figure stores trying to push past growth plateaus. The problems at different scales look different but share the same structural origins.",
    "After fifty-plus consulting engagements, the patterns are clear. Most conversion problems come from a small set of predictable causes - unclear value propositions, product pages that answer the wrong questions, checkout friction that exists because no one tested removing it, and pricing presentations that undermine purchase confidence.",
    "What I notice about ecommerce advice online is that it is mostly either too generic to act on or too tactical without the strategic context that explains when a tactic applies. Knowing which tactic applies to which problem is the actual skill.",
    "Ecommerce Edge is where I publish the frameworks and analyses from working inside actual stores with actual revenue at stake. Every conversion tactic gets evaluated in the context of why it works, when it applies, and what the evidence from real stores looks like.",
  ],
  "insightinsure": [
    "I started my career at a captive insurance agency, which means I was licensed to sell products from a single carrier. The job taught me the fundamentals of underwriting and coverage, but it also showed me something about incentives that I could not unsee - when you only sell one carrier's products, your job is not to find the client the right coverage. Your job is to make the carrier's products fit the client.",
    "At twenty-eight I switched to independent brokerage. The difference was immediate. I could shop multiple carriers for each client, and the conversations changed completely. I started telling clients things their previous agents had never told them - not because those agents were dishonest, but because they literally could not offer the alternative.",
    "Eighteen years as an independent broker has given me a clear picture of the coverage decisions most people get wrong. Term life buyers choosing the wrong structure. Homeowners underinsuring for replacement cost. Business owners without the specific riders that matter for their actual exposures.",
    "Most insurance content online is written by people who make money when you buy a policy. That shapes what gets written. Coverage comparisons highlight features that make a carrier's product look good rather than asking what the client's actual risk looks like.",
    "Insight Insure has no carrier allegiances and no referral fees from insurance companies. I write about coverage the way I talk to clients - starting with what they actually need and working backward to what product delivers it. The goal is an informed buyer who understands what they are paying for.",
  ],
  "sellit-ca": [
    "I bought my first rental property at twenty-seven with money saved over four years working as a paralegal. It was a duplex in a mid-tier market that needed work. The work cost more than planned and the first tenant gave me an education in lease enforcement I could not have gotten any other way.",
    "I went to law school while holding that property. Real estate law was not my initial focus, but the intersection of contract law, landlord-tenant regulation, and property rights kept pulling me back. I graduated and specialized in exactly that intersection.",
    "Fourteen doors across three markets and nine years as a practicing attorney. The combination is unusual enough that clients specifically seek it out. They want to know what a deal looks like on paper and what it looks like when something goes wrong legally. Those are often two very different analyses.",
    "What I have seen consistently in real estate investing content is a gap between the numbers analysis and the legal reality. Underwriting models show projected cash flow, but they rarely price in the legal exposure that comes with certain deal structures, certain markets, or certain tenant profiles.",
    "Mash Estate is where I publish the combined analysis - deal structures and their legal implications, market reads that consider both financial and regulatory environments, and the landmines in due diligence that most investors do not know to look for.",
  ],
  "newborniq": [
    "I went into nursing knowing I wanted to work with newborns. The NICU track requires additional training beyond the RN, and I pursued it immediately after graduating. The NICU is unlike any other unit - the pace, the stakes, and the weight of caring for families in their most vulnerable moments shape you permanently.",
    "Twelve years in the NICU means I have watched thousands of parents navigate the most overwhelming weeks of their lives. In those twelve years I have also watched the quality of information available to parents outside the hospital become increasingly unreliable as social media filled the space once held by consistent public health messaging.",
    "The patterns in what new parents believe about infant care worry me. Sleep advice that contradicts current safe sleep guidelines. Feeding advice that creates anxiety around normal hunger cues. Developmental expectations based on what parents want to be true rather than what the research shows.",
    "Pediatric evidence has moved significantly in the past decade on pacifier use, safe sleep environments, responsive feeding, and early allergen introduction. Parents reading content from five years ago are reading outdated guidance.",
    "Newborn IQ is built around what current pediatric evidence actually supports. I write from twelve years of clinical experience and ongoing review of published research. The goal is content a NICU nurse would actually recommend - practical, calm, accurate, and free of the anxiety-amplification that defines too much of what new parents read.",
  ],
  "passivewealthguide": [
    "I started investing at twenty-four on a teacher's salary, which meant starting very small. My first investment was a low-cost index fund I contributed to monthly, not because I had a sophisticated strategy but because it was the simplest thing I could do without yet understanding the alternatives. That simplicity turned out to serve me well.",
    "Over time I added to the strategy - dividend-paying stocks, then REITs, then eventually a small rental property when I had saved enough for a down payment. Each layer added passive income and added complexity. I spent years understanding each one before adding the next.",
    "I retired at forty-one. The honest version of that story is that it took fifteen years of consistent investing, deliberate spending, and several decisions that looked conservative at the time but preserved capital I later deployed at better prices. It was not fast, and it did not involve a viral moment.",
    "What bothers me about passive income content online is the timeline problem. Almost everything presents passive income as achievable in months, with strategies that require significant capital, significant time misclassified as passive, or significant luck. The realistic timeline is measured in years, not months.",
    "Passive Wealth Guide is the version for people who want the actual math. How long does it realistically take to build a specific passive income amount from a specific starting capital? What are the tax implications at each stage? Which strategies are genuinely passive and which require ongoing management? I went through all of it.",
  ],
  "mochapoo-pets": [
    "I grew up in a house that always had dogs, and by the time I was choosing a career path, studying veterinary medicine felt less like a choice and more like an inevitability. I have been practicing for fourteen years now, and the work still carries the same weight it did when I started.",
    "Doodle mixes started appearing in my practice about ten years ago as a trickle and became a flood within three years. Mochapoos specifically became one of my most common patients. I got to know the breed's health patterns, behavioral tendencies, and nutritional sensitivities through hundreds of individual cases.",
    "What concerns me about the information environment for doodle breed owners is that most of it is produced by breeders with a financial interest in presenting these dogs as low-maintenance and universally adaptable. The reality is more complicated. Mixed breeds can inherit health tendencies from both parent breeds that owners are not prepared for.",
    "Veterinary perspective differs from breeder perspective in specific ways. I see the dogs owners bring in with the problems that were not in the breed description - anxiety in under-socialized dogs, dental problems common in small doodle mixes, ear infections that come with the coat type. That clinical exposure shapes what I write about.",
    "MochaPoo Pets is the resource I recommend to my clients who want to go deeper than the breeder packet. Science-backed care guides, honest health information, nutrition graded by actual canine research, and behavioral guidance from clinical observation rather than aspirational breed descriptions.",
  ],
  "sightreadingacademy": [
    "I started playing piano at five years old, and by the time I was twelve I knew I was going to pursue it seriously. That path led to conservatory training, then to Juilliard for graduate study, then to a concert performance career spanning fifteen years across three continents.",
    "Performing at a high level requires reading at a high level. New repertoire arrives constantly, collaborative work requires reading at first meeting, and competitions often include sight-reading components. I spent years developing a methodology that worked under pressure - not just in slow practice sessions but in real performance situations.",
    "When I transitioned into conservatory teaching, I found a consistent pattern in my students. They had been practicing sight-reading, but practicing it wrong. They reinforced bad habits - playing too slowly, self-correcting in ways that interrupted flow, not building the pattern recognition that fluency requires.",
    "The research on skill acquisition in music is clear about what builds fluency and what builds avoidance behavior. Fluency comes from reading at or slightly above performance speed, from working with unfamiliar material at high frequency, and from building a mental lexicon of common harmonic and melodic patterns.",
    "Sight Reading Academy is the methodology I developed through performance experience and refined through twenty years of conservatory teaching. It is structured, progressive, and grounded in how musical pattern recognition actually develops. Whether you are building foundations or removing a specific ceiling, the approach scales.",
  ],
  "dalmend-home": [
    "I studied interior design formally and started my career doing residential renovations for clients preparing homes for sale. That staging work gave me a perspective most decorators never develop - the financial relationship between design decisions and property value. When you are designing a space that needs to sell, aesthetic choices have measurable financial consequences.",
    "After four years of that work I started investing in properties myself. Buying, renovating, and selling gave me a second education in the gap between what looks good and what adds value. Some renovations I had been designing for clients for years returned almost nothing at resale. Others returned significantly more than they cost.",
    "Eleven years as both a designer and an investor has produced a fairly clear framework for which decisions pay off and which are pure aesthetic preference. Kitchen updates return above average. Master bathroom updates return well in certain markets. Landscaping returns less than most homeowners believe.",
    "What I find missing from most interior design content is the financial lens. Design media is built around what looks beautiful on camera, not what holds its value, not what improves livability in measurable ways, not what a buyer will actually pay more for.",
    "Dalmend Home is where both lenses are applied simultaneously. I write about design with the aesthetic rigor of a trained designer and the financial scrutiny of someone who has bought, renovated, and sold six properties. If a change looks beautiful but does not improve livability or value, I will tell you to skip it.",
  ],
  "makeupcraft": [
    "I started my career behind a makeup counter at a department store, which turned out to be an excellent education in the gap between how products are marketed and how they actually perform across a range of skin types and tones. Three years on that floor taught me foundation matching, color theory application, and the reality that no single product works universally.",
    "I trained formally as a makeup artist, built my kit, and started doing bridal and event work while building toward editorial and commercial. The career progression across fashion weeks, editorial shoots, and film sets over sixteen years exposed me to techniques that home-use tutorials rarely cover - how light interacts with different skin surfaces, how makeup reads on camera versus in person.",
    "Teaching other artists became part of my work about seven years into my career. Through teaching I realized how much bad information was circulating about technique. The sponsored tutorial ecosystem had created artists who changed products constantly but had shallow understanding of the underlying applications.",
    "The fundamental problem in beauty content is that it is almost universally product-focused because product focus generates affiliate income and brand partnerships. The result is that millions of people are buying new products to solve problems that are actually about technique.",
    "Makeup Craft is technique-first. I write about specific products when they solve a genuine problem that others in the category do not solve as well. But the majority of what I publish is about application - how to build coverage without caking, how to set for longevity across different skin types, how to blend in ways that read naturally in real light.",
  ],
  "travelverge": [
    "I took my first solo trip at twenty-four with three weeks of savings and a ticket to Southeast Asia. I had no plan beyond the first night's accommodation. That trip was by turns wonderful and chaotic, and within a week of returning I was planning the next one. That pattern has continued for nine years across sixty-three countries.",
    "All of those countries were funded independently. No press trips, no destination board invitations, no sponsored accommodations. This is not a moral stance - it is simply how I have traveled, and it has shaped what I write. When I stayed somewhere terrible, I paid for it myself. When I found something exceptional, no one was paying me to say so.",
    "What I notice about travel content now is the convergence problem. The same twenty destinations appear in everyone's feeds because they photograph well and brands want association with beauty rather than complexity. The variety of travel experience is compressed into a narrow aesthetic.",
    "Nine years of independent travel has also produced mistakes that most travel content does not discuss - entering a country through the wrong crossing and getting held for hours, booking accommodation in a neighborhood that looked fine on a map and was not fine in person, timing a visit badly because I trusted outdated online guidance.",
    "Travel Verge is built on specificity and honesty. When I recommend a route it is because I traveled it recently, on my own money, and assessed the actual experience against the commonly available description. When a destination has changed from how it is still described online, I will say so.",
  ],
  "mashestate-construction": [
    "I started in construction as an apprentice carpenter straight out of high school. The work was physical, the hours were long, and within a year I understood the basic economics of a construction project in a way no classroom could have taught me - material costs, labor hours, sequencing errors, and the compounding effect of starting something out of order.",
    "I got my general contractor license at twenty-eight after years working in framing, finish carpentry, and project supervision. My first company was small - three crews, mostly residential renovation. The first few years were profitable and chaotic. By year five I had built the systems that made the chaos manageable.",
    "Twenty-two years in the field means I have seen every way a construction project goes wrong. Bad bids that seemed low because they excluded scope that was always going to be needed. Change orders used as profit centers. Permits pulled for work done incorrectly then covered over.",
    "What I have noticed is that property owners lose money on construction projects not because they are uninformed, but because they lack the framework to evaluate what they are being told. A homeowner who does not understand construction sequencing cannot evaluate whether a timeline is realistic.",
    "Mash Construction is the resource I give to every property owner client before they start a project. An informed owner catches problems earlier, asks better questions, and gets better work at better prices. The goal is not to eliminate the need for a good contractor - it is to make you the kind of client that a good contractor wants to work with.",
  ],
  "kanona-events": [
    "I started in the events industry at twenty-three as a venue coordinator for a mid-size conference center. The job required managing vendor relationships, coordinating setups, and serving as the on-site problem solver for planners often running events for the first time. In three years I watched hundreds of events and catalogued everything that went wrong and why.",
    "I launched my own event production company at twenty-nine with a small team focused on corporate and private events above a certain production value. The business grew steadily because we were reliable in a way that is apparently rare in the industry - vendors showed up, timelines held, and the client's vision was actually executed rather than approximated.",
    "Six hundred events over twelve years covers a lot of ground: corporate conferences, product launches, fundraising galas, large private celebrations, and formats in between. The root causes of failures are remarkably consistent. Budget overruns almost always trace to scope not clearly defined in the contract phase. Day-of chaos almost always traces to vendor communication inadequate in the weeks before the event.",
    "What I find missing in event planning content is the insider perspective on vendor relationships. How caterers actually price, where the margin is in a production quote, what a venue coordinator can and will do for you depending on their incentives. This information is not secret - it lives with people who have spent years on the other side of the table.",
    "Kanona Projects is the manual I assembled from twelve years of production experience. The budgeting frameworks, the vendor selection criteria, the timeline architecture that distinguishes professional events from amateur ones. Whether you are a professional planner building your process or a host running your first large event, the goal is the same.",
  ],
}

# ── Per-site Pexels search query for banner images ─────────────────────────────
PEXELS_QUERIES = {
  "cryptopulse":            "cryptocurrency trading charts financial data",
  "tradingtechreview":      "trading software computer screens code",
  "carverge":               "electric vehicle car charging modern automotive",
  "aimarketingpro":         "digital marketing laptop analytics data",
  "onlinebizpro":           "entrepreneur laptop business startup office",
  "sportiqpro":             "athlete strength training sports performance",
  "datingedge":             "couple relationship psychology conversation",
  "fitpulsepro":            "gym workout fitness training exercise",
  "supplementverge":        "nutrition supplements vitamins health science",
  "ecommerceedge":          "online shopping ecommerce website store",
  "insightinsure":          "insurance documents financial planning office",
  "sellit-ca":        "real estate house property investment",
  "newborniq":              "newborn baby infant care peaceful sleeping",
  "passivewealthguide":     "investing money financial growth savings",
  "mochapoo-pets":          "doodle puppy dog cute fluffy playful",
  "sightreadingacademy":    "piano keyboard sheet music playing",
  "dalmend-home":           "interior design modern living room decor",
  "makeupcraft":            "makeup beauty cosmetics professional brushes",
  "travelverge":            "travel landscape adventure mountains destination",
  "mashestate-construction":"construction building renovation architecture",
  "kanona-events":          "event planning celebration gala corporate dinner",
}


# ── Shared template helpers ────────────────────────────────────────────────────
def _shell_body_colors(stem, fallback_text="#1a1a1a", fallback_bg="#ffffff"):
    """Read the homepage template and return the actual body{background, color}
    pair (resolving one level of var(--name)) so generated pages (about, legal)
    use ink that always contrasts with the page background, even if the SITES
    color tokens are tuned for the nav region instead of the body. Prevents
    invisible-headline bugs like MindFrame's about page rendering cream on cream."""
    import re as _re
    p = layout_shell.template_path(stem)
    if not p.exists():
        return fallback_text, fallback_bg
    txt = p.read_text(encoding="utf-8")
    def _resolve(val):
        val = val.strip()
        if val.startswith("var("):
            name = val[4:-1].split(",")[0].strip()
            m = _re.search(rf"{_re.escape(name)}\s*:\s*(#[0-9a-fA-F]{{3,8}})", txt)
            return m.group(1) if m else None
        if val.startswith("#"):
            return val
        return None
    color = bg = None
    body = _re.search(r"\bbody\s*\{([^}]*)\}", txt)
    if body:
        block = body.group(1)
        mc = _re.search(r"\bcolor\s*:\s*([^;]+);", block)
        mb = _re.search(r"\bbackground(?:-color)?\s*:\s*([^;]+);", block)
        if mc: color = _resolve(mc.group(1))
        if mb:
            # background may be "var(--paper)" or "var(--paper) url(...) ..." - take first token
            first = mb.group(1).strip().split()[0]
            bg = _resolve(first)
    return color or fallback_text, bg or fallback_bg


def _ink_for(s):
    """Page-body text color guaranteed to contrast with the page background.
    Used by gen_about / legal pages instead of raw s['text']."""
    text, _ = _shell_body_colors(s['id'], fallback_text=s.get('text', '#1a1a1a'))
    return text


def _page_bg_for(s):
    _, bg = _shell_body_colors(s['id'], fallback_bg=s.get('surface') or s.get('bg', '#ffffff'))
    return bg


def _story_html(s, css_class='abt-p'):
    """Render story paragraphs from STORIES dict, fallback to bio1/bio2."""
    paras = STORIES.get(s['id'], [s['bio1'], s['bio2']])
    return '\n    '.join(f'<p class="{css_class}">{p}</p>' for p in paras)


def _pexels_banner(height='260px', extra=''):
    """Full-width banner: Pexels photo if key set, else Picsum stock photo."""
    return f"""<!-- hero-banner -->
<div id="pxl-wrap" style="width:100%;height:{height};overflow:hidden;position:relative;background:var(--bg2);{extra}">
  <img id="pxl-img" style="width:100%;height:100%;object-fit:cover;opacity:0;transition:opacity .8s;display:block;" alt="">
  <a id="pxl-cred" href="https://www.pexels.com" target="_blank" rel="noopener" style="position:absolute;bottom:6px;right:10px;font-size:10px;color:rgba(255,255,255,.5);opacity:0;transition:opacity .6s;text-decoration:none;">Photo: Pexels</a>
</div>"""


def _pexels_js(s):
    """Banner loader: tries Pexels, Unsplash (if keys set), falls back to Picsum."""
    q    = PEXELS_QUERIES.get(s['id'], s['category'])
    seed = abs(hash(s['id'])) % 1000
    sources = s.get("image_sources", ["pexels", "unsplash"])  # per-site override
    src_js = str(sources)
    return f"""/* banner loader: pexels → unsplash → picsum */
(function(){{
  var el=document.getElementById('pxl-img');
  var cr=document.getElementById('pxl-cred');
  if(!el)return;
  var SOURCES={src_js};
  var Q=encodeURIComponent('{q}');
  var FALLBACK='https://picsum.photos/seed/{seed}/1400/400';
  function showImg(src,cred){{
    el.onload=function(){{el.style.opacity='1';if(cred&&cr){{cr.textContent=cred;cr.style.opacity='1';}}}};
    el.src=src;
  }}
  function tryUnsplash(){{
    var uk=localStorage.getItem('unsplashKey');
    if(!uk){{showImg(FALLBACK,'');return;}}
    fetch('https://api.unsplash.com/photos/random?query='+Q+'&count=1&orientation=landscape&client_id='+uk)
      .then(function(r){{return r.json();}}).then(function(d){{
        var p=Array.isArray(d)?d[0]:d;
        if(p&&p.urls&&p.urls.regular){{showImg(p.urls.regular,'Photo: '+((p.user&&p.user.name)||'Unsplash')+' / Unsplash');}}
        else{{showImg(FALLBACK,'');}}
      }}).catch(function(){{showImg(FALLBACK,'');}});
  }}
  function tryPexels(){{
    var k=localStorage.getItem('pexelsKey');
    if(!k){{if(SOURCES.indexOf('unsplash')>=0)tryUnsplash();else showImg(FALLBACK,'');return;}}
    fetch('https://api.pexels.com/v1/search?query='+Q+'&per_page=5&orientation=landscape',{{headers:{{Authorization:k}}}})
      .then(function(r){{return r.json();}}).then(function(d){{
        if(d.photos&&d.photos[0]){{showImg(d.photos[0].src.large,'Photo: Pexels');}}
        else if(SOURCES.indexOf('unsplash')>=0){{tryUnsplash();}}
        else{{showImg(FALLBACK,'');}}
      }}).catch(function(){{if(SOURCES.indexOf('unsplash')>=0)tryUnsplash();else showImg(FALLBACK,'');}});
  }}
  if(SOURCES.indexOf('pexels')>=0){{tryPexels();}}
  else if(SOURCES.indexOf('unsplash')>=0){{tryUnsplash();}}
  else{{showImg(FALLBACK,'');}}
}})();"""


# ── Contributor profiles (randomly assigned 4-5 per about page) ───────────────
CONTRIBUTORS = [
    {"name": "Rachel Kim",      "role": "Contributing Analyst",     "avatar": "RK", "bio": "Former hedge fund researcher. Covers quantitative methods and market microstructure. Has contributed to three academic finance papers."},
    {"name": "Marcus Webb",     "role": "Senior Contributor",       "avatar": "MW", "bio": "15 years in institutional sales at two major banks. Writes about macro dynamics and how they translate to retail positioning."},
    {"name": "Priya Nair",      "role": "Research Contributor",     "avatar": "PN", "bio": "Data scientist turned independent writer. Builds the models, then explains what they actually mean in plain language."},
    {"name": "Daniel Osei",     "role": "Field Correspondent",      "avatar": "DO", "bio": "On the ground covering conferences, product launches, and industry events. Focuses on what the press releases leave out."},
    {"name": "Sofia Reyes",     "role": "Editorial Contributor",    "avatar": "SR", "bio": "Spent eight years as a financial journalist before going independent. Strong background in regulatory and policy reporting."},
    {"name": "James Thorne",    "role": "Technical Contributor",    "avatar": "JT", "bio": "Full-stack developer who switched to financial writing. Covers the engineering reality behind products and platforms."},
    {"name": "Amara Okafor",    "role": "Strategy Contributor",     "avatar": "AO", "bio": "Portfolio manager background. Writes about position sizing, risk management, and the behavioral side of long-term investing."},
    {"name": "Lena Fischer",    "role": "International Contributor","avatar": "LF", "bio": "Based in Frankfurt. Covers European regulatory developments, cross-border market dynamics, and emerging market capital flows."},
    {"name": "Tom Nakamura",    "role": "Data Contributor",         "avatar": "TN", "bio": "Ex-quant at a Chicago prop firm. Builds custom scrapers and datasets, then writes about what the data actually shows."},
    {"name": "Claire Sutton",   "role": "Industry Contributor",     "avatar": "CS", "bio": "Worked in PR for major financial brands before switching sides. Understands how the narrative gets constructed, and how to cut through it."},
]

CONTRIBUTOR_COMMENTS = [
    {"author": "Mike H.",    "text": "The level of detail here is what keeps me coming back. You actually back up the claims instead of just asserting them."},
    {"author": "Serena T.",  "text": "I have shared this with three colleagues already. The kind of analysis that used to be locked behind expensive research subscriptions."},
    {"author": "Chris V.",   "text": "Refreshing to read something that acknowledges uncertainty instead of pretending everything is obvious in hindsight."},
    {"author": "Denise L.",  "text": "I have been following this site for over a year. The consistency and quality have only gone up. Very few places I can say that about."},
    {"author": "Raj P.",     "text": "The data-first approach here is exactly what I was looking for. Most analysis I find online is opinion dressed up as research."},
    {"author": "Hannah O.",  "text": "Came for one article, stayed for the whole archive. The depth on topics most outlets treat as afterthoughts is impressive."},
    {"author": "Brett W.",   "text": "I appreciate that corrections get made openly and visibly. That kind of intellectual honesty is rare and worth rewarding with attention."},
    {"author": "Nadia F.",   "text": "The writing here treats readers as intelligent adults. No dumbing down, no sensationalism, just clear analysis."},
    {"author": "Omar K.",    "text": "I have read things here that changed how I think about the field. That is a high bar and this site clears it regularly."},
    {"author": "Julia M.",   "text": "Bookmarked every major article this site has published. My actual reference library for this topic, not just casual reading."},
]

import hashlib as _hs

def _site_contributors(s, count=4):
    """Pick count deterministic contributors for a site (same every run).
    If the site declares its own author_names list with 2+ entries, use those
    real names with neutral roles (no fabricated bios). Sites with a single
    declared author (or no list) get an empty list so the about page can omit
    the Contributors section entirely - this avoids the old behavior of
    showing finance-themed personas like 'Portfolio manager' on a dental
    journal."""
    declared = [n for n in (s.get('author_names') or []) if n and n.strip()]
    if len(declared) >= 2:
        # Skip the primary author (already shown in the hero card)
        primary = s.get('author') or s.get('default_author') or declared[0]
        rest = [n for n in declared if n != primary]
        if not rest:
            return []
        role = "Contributor"
        return [
            {
                "name": n,
                "role": role,
                "avatar": ''.join(w[0].upper() for w in n.split()[:2]),
                "bio": "",
            }
            for n in rest[:count]
        ]
    # Single-author site - do not invent contributors.
    if len(declared) <= 1:
        return []
    # Fallback (should not reach): old generic pool.
    seed = int(_hs.md5(s['id'].encode()).hexdigest(), 16)
    pool = CONTRIBUTORS[:]
    for i in range(len(pool)-1, 0, -1):
        j = seed % (i+1); pool[i], pool[j] = pool[j], pool[i]; seed //= (i+1)
    return pool[:count]

def _site_comments(s, count=5):
    """Pick count deterministic comments for a site."""
    seed = int(_hs.md5((s['id']+'c').encode()).hexdigest(), 16)
    pool = CONTRIBUTOR_COMMENTS[:]
    for i in range(len(pool)-1, 0, -1):
        j = seed % (i+1); pool[i], pool[j] = pool[j], pool[i]; seed //= (i+1)
    return pool[:count]

def _contributors_html(s, card_bg='#0d1410', border='#1e3024', text='#ffffff', muted='#4d7059', accent='#3ecf8e'):
    contributors = _site_contributors(s, 4)
    cards = []
    for c in contributors:
        cards.append(f"""<div style="background:{card_bg};border:1px solid {border};border-radius:10px;padding:16px;display:flex;gap:12px;align-items:flex-start">
      <div style="width:40px;height:40px;border-radius:50%;background:{accent};color:#000;font-size:13px;font-weight:800;display:flex;align-items:center;justify-content:center;flex-shrink:0">{c['avatar']}</div>
      <div>
        <div style="font-size:14px;font-weight:700;color:{text}">{c['name']}</div>
        <div style="font-size:11px;color:{accent};margin-bottom:5px;font-weight:600">{c['role']}</div>
        <div style="font-size:12px;color:{muted};line-height:1.6">{c['bio']}</div>
      </div>
    </div>""")
    return '\n    '.join(cards)

def _comments_html(s, bg='#0d1410', border='#1e3024', text='#b8d4c0', muted='#4d7059', accent='#3ecf8e'):
    comments = _site_comments(s, 5)
    items = []
    for i, c in enumerate(comments):
        items.append(f"""<div style="padding:14px 0;border-bottom:1px solid {border}{''}">
      <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px">
        <div style="width:28px;height:28px;border-radius:50%;background:{accent}22;border:1px solid {accent}44;color:{accent};font-size:11px;font-weight:700;display:flex;align-items:center;justify-content:center">{c['author'][0]}</div>
        <span style="font-size:13px;font-weight:600;color:{text}">{c['author']}</span>
        <span style="font-size:10px;color:{muted};margin-left:auto">Verified reader</span>
      </div>
      <div style="font-size:13px;color:{text};line-height:1.65;padding-left:36px">{c['text']}</div>
    </div>""")
    last = items.pop()
    items.append(last.replace('border-bottom:1px solid ' + border, 'border-bottom:none'))
    return '\n    '.join(items)

# ── Shared about-section builder ──────────────────────────────────────────────
def _about_block(s, bg, border, text, muted, accent, mono_font=''):
    """Author + site-mission section used by every homepage template."""
    ini = ''.join(w[0].upper() for w in s['author'].split()[:2])
    mf  = f"font-family:{mono_font};" if mono_font else ""
    return f"""<div style="background:{bg};border-top:1px solid {border};border-bottom:1px solid {border};padding:40px">
  <div style="max-width:800px;margin:0 auto">
    <div style="{mf}font-size:10px;color:{accent};text-transform:uppercase;letter-spacing:3px;margin-bottom:20px">// about this publication</div>
    <div style="display:grid;grid-template-columns:60px 1fr;gap:20px;align-items:start;margin-bottom:24px">
      <div style="width:56px;height:56px;border-radius:50%;background:{accent};display:flex;align-items:center;justify-content:center;font-size:18px;font-weight:800;color:#000;flex-shrink:0;letter-spacing:-1px">{ini}</div>
      <div>
        <div style="font-size:16px;font-weight:700;color:{text};margin-bottom:2px">{s['author']}</div>
        <div style="font-size:12px;color:{accent};margin-bottom:14px;font-weight:600">{s['author_title']}</div>
        <p style="font-size:14px;color:{muted};line-height:1.85;margin-bottom:12px">{s['bio1']}</p>
        <p style="font-size:14px;color:{muted};line-height:1.85">{s['bio2']}</p>
      </div>
    </div>
    <a href="about.html" style="display:inline-block;border:1px solid {accent};color:{accent};padding:8px 20px;border-radius:3px;font-size:12px;font-weight:700;text-decoration:none;{mf}text-transform:uppercase;letter-spacing:1px;transition:all .2s">Full bio →</a>
  </div>
</div>"""

# ── CSS variables block ────────────────────────────────────────────────────────
def css_vars(s):
    return f"""  --bg:{s['bg']};--bg2:{s['bg2']};--sur:{s['surface']};
  --pri:{s['primary']};--pri2:{s['primary2']};
  --txt:{s['text']};--mut:{s['muted']};--brd:{s['brd']};
  --fh:{s['font_head']};--fb:{s['font_body']};--fm:{s['font_mono']};"""

# ── TEMPLATE: TERMINAL (Bloomberg-style news homepage) ────────────────────────
def terminal_index(s):
    # Custom template override  -  if templates/{id}-index.html exists, use it directly
    _tmpl = BASE / "templates" / f"{s['id']}-index.html"
    if _tmpl.exists():
        return _tmpl.read_text(encoding="utf-8")
    cv   = css_vars(s)
    ini  = ''.join(w[0].upper() for w in s['author'].split()[:2])
    seed = abs(hash(s['id'])) % 1000
    pxjs = _pexels_js(s)
    s1,s2,s3,s4,s5,s6,s7,s8,s9,s10 = [seed+i for i in range(1,11)]
    q    = PEXELS_QUERIES.get(s['id'], s['category']).replace(' ','+')
    # SVG icons  -  no emoji anywhere
    ico_signal = '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round"><path d="M2 18.5a16 16 0 0 1 20 0"/><path d="M5.5 15a11 11 0 0 1 13 0"/><path d="M9 11.5a6 6 0 0 1 6 0"/><circle cx="12" cy="20" r="1.5" fill="currentColor"/></svg>'
    ico_chain  = '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="9" width="5" height="6" rx="1"/><rect x="9.5" y="9" width="5" height="6" rx="1"/><rect x="17" y="9" width="5" height="6" rx="1"/><line x1="7" y1="12" x2="9.5" y2="12"/><line x1="14.5" y1="12" x2="17" y2="12"/></svg>'
    ico_gear   = '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M12 1v3M12 20v3M4.22 4.22l2.12 2.12M17.66 17.66l2.12 2.12M1 12h3M20 12h3M4.22 19.78l2.12-2.12M17.66 6.34l2.12-2.12"/></svg>'
    ico_cross  = '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round"><circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="3.5"/><line x1="12" y1="3" x2="12" y2="8.5"/><line x1="12" y1="15.5" x2="12" y2="21"/><line x1="3" y1="12" x2="8.5" y2="12"/><line x1="15.5" y1="12" x2="21" y2="12"/></svg>'
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{s['name']}: {s['tagline']}</title>
<meta name="description" content="{s['hero_sub']}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Space+Mono:ital,wght@0,400;0,700;1,400&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
:root{{{cv}--fh:'Space Grotesk',system-ui,sans-serif;--fm:'Space Mono',monospace;}}
html{{scroll-behavior:smooth}}
body{{background:var(--bg);color:var(--txt);font-family:'Space Grotesk',system-ui,sans-serif;font-size:15px;line-height:1.65;min-height:100vh;overflow-x:hidden}}
a{{color:inherit;text-decoration:none}}
img{{display:block;max-width:100%}}

/* ── ticker ── */
.tk-bar{{background:#020d06;border-bottom:1px solid #0d2b18;height:38px;display:flex;align-items:center;overflow:hidden;width:100%}}
.tk-label{{font-family:var(--fm);font-size:9px;font-weight:700;color:#020d06;background:var(--pri);padding:0 14px;height:100%;display:flex;align-items:center;flex-shrink:0;letter-spacing:2px;text-transform:uppercase;gap:5px}}
.tk-dot{{width:7px;height:7px;border-radius:50%;background:#020d06;animation:blink 1.2s ease-in-out infinite}}
@keyframes blink{{0%,100%{{opacity:1}}50%{{opacity:.2}}}}
.tk-viewport{{flex:1;overflow:hidden}}
.tk-track{{display:flex;white-space:nowrap;animation:ticker-scroll 40s linear infinite}}
.tk-track:hover{{animation-play-state:paused}}
@keyframes ticker-scroll{{from{{transform:translateX(0)}}to{{transform:translateX(-50%)}}}}
.tk-item{{font-family:var(--fm);font-size:11px;color:#4a7a5a;display:inline-flex;gap:7px;align-items:center;padding:0 22px;border-right:1px solid #0d2b18}}
.tk-sym{{color:#a0cfb0;font-weight:700;letter-spacing:.5px}}
.tk-up{{color:var(--pri);font-weight:700}}
.tk-dn{{color:#ff5252;font-weight:700}}

/* ── nav ── */
.nav{{background:#020d06;border-bottom:1px solid #0d2b18;position:sticky;top:0;z-index:100}}
.nav-inner{{max-width:1280px;margin:0 auto;padding:0 20px;display:flex;align-items:center;height:58px;gap:0}}
.nav-logo{{font-size:20px;font-weight:700;color:var(--pri);margin-right:40px;flex-shrink:0;letter-spacing:-0.5px}}
.nav-logo span{{font-family:var(--fm);font-size:10px;color:#2a5a38;font-weight:400;margin-left:6px;letter-spacing:1px;text-transform:uppercase}}
.nav-links{{display:flex;gap:0;height:100%;flex:1}}
.nav-links a{{font-family:var(--fm);font-size:11px;font-weight:700;color:#3a6a48;text-transform:uppercase;letter-spacing:1px;padding:0 14px;height:100%;display:flex;align-items:center;border-bottom:2px solid transparent;transition:all .2s;margin-bottom:-1px}}
.nav-links a:hover,.nav-links a.active{{color:var(--pri);border-bottom-color:var(--pri)}}
.nav-right{{display:flex;align-items:center;gap:14px;flex-shrink:0}}
.nav-date{{font-family:var(--fm);font-size:10px;color:#2a5a38}}
.nav-subscribe{{font-family:var(--fm);font-size:10px;font-weight:700;color:#020d06;background:var(--pri);padding:6px 14px;border-radius:2px;text-transform:uppercase;letter-spacing:1px;white-space:nowrap}}
.nav-burger{{display:none;flex-direction:column;gap:5px;cursor:pointer;padding:8px;background:none;border:none}}
.nav-burger span{{width:22px;height:2px;background:var(--pri);border-radius:1px;display:block;transition:all .3s}}
.nav-mobile{{display:none;position:absolute;top:100%;left:0;right:0;background:#020d06;border-bottom:1px solid #0d2b18;flex-direction:column;padding:12px 0;z-index:99}}
.nav-mobile.open{{display:flex}}
.nav-mobile a{{font-family:var(--fm);font-size:12px;font-weight:700;color:#3a6a48;text-transform:uppercase;letter-spacing:1px;padding:12px 24px;border-bottom:1px solid #0a1e10;display:block}}
.nav-mobile a:last-child{{border-bottom:none}}
.nav-mobile a:hover{{color:var(--pri);background:#030f07}}

/* ── SECTION 1: HERO GRID ── */
.hero-section{{background:#020d06;border-bottom:1px solid #0d2b18}}
.hero-wrap{{max-width:1280px;margin:0 auto;display:grid;grid-template-columns:1fr 380px;min-height:520px}}
.hero-feat{{position:relative;overflow:hidden;display:block}}
.hero-feat-img{{width:100%;height:100%;object-fit:cover;display:block;opacity:0;transition:opacity 1s;min-height:520px}}
.hero-feat-ovl{{position:absolute;inset:0;background:linear-gradient(to top,rgba(1,8,4,.98) 0%,rgba(1,8,4,.6) 45%,rgba(1,8,4,.1) 100%)}}
.hero-feat-body{{position:absolute;bottom:0;left:0;right:0;padding:36px 40px}}
.hero-badge{{display:inline-flex;align-items:center;gap:6px;font-family:var(--fm);font-size:9px;font-weight:700;color:#020d06;background:var(--pri);padding:4px 10px;border-radius:1px;text-transform:uppercase;letter-spacing:2px;margin-bottom:16px}}
.hero-h1{{font-size:clamp(22px,3.5vw,42px);font-weight:700;line-height:1.1;color:#e8f5ec;margin-bottom:12px;letter-spacing:-0.5px}}
.hero-desc{{font-size:14px;color:#5a8a6a;line-height:1.7;margin-bottom:20px;max-width:560px}}
.hero-byline{{font-family:var(--fm);font-size:10px;color:#2a5a38;display:flex;align-items:center;gap:12px}}
.hero-cta{{font-family:var(--fm);font-size:11px;font-weight:700;color:#020d06;background:var(--pri);padding:10px 20px;border-radius:2px;text-transform:uppercase;letter-spacing:1px;flex-shrink:0;transition:opacity .2s}}
.hero-cta:hover{{opacity:.85}}

/* sub-stories column */
.hero-sub-col{{display:flex;flex-direction:column;border-left:1px solid #0d2b18;background:#030f07}}
.sub-story{{display:grid;grid-template-columns:110px 1fr;gap:0;border-bottom:1px solid #0d2b18;flex:1;min-height:0;overflow:hidden;transition:background .2s;cursor:pointer}}
.sub-story:last-child{{border-bottom:none}}
.sub-story:hover{{background:#050f08}}
.sub-story-img{{width:110px;height:100%;min-height:120px;object-fit:cover;display:block}}
.sub-story-body{{padding:16px 18px;display:flex;flex-direction:column;gap:5px;justify-content:center}}
.sub-badge{{font-family:var(--fm);font-size:8px;font-weight:700;color:var(--pri);text-transform:uppercase;letter-spacing:2px}}
.sub-title{{font-size:13px;font-weight:600;line-height:1.35;color:#c0ddc8;transition:color .2s}}
.sub-story:hover .sub-title{{color:var(--pri)}}
.sub-date{{font-family:var(--fm);font-size:10px;color:#2a5a38;margin-top:3px}}

/* ── SECTION 2: VALUE PROPS ── */
.vp-section{{background:#030f07;border-bottom:1px solid #0d2b18}}
.vp-wrap{{max-width:1280px;margin:0 auto;display:grid;grid-template-columns:repeat(4,1fr)}}
.vp-item{{padding:24px 28px;border-right:1px solid #0d2b18;display:flex;align-items:flex-start;gap:14px}}
.vp-item:last-child{{border-right:none}}
.vp-icon{{width:40px;height:40px;flex-shrink:0;display:flex;align-items:center;justify-content:center;background:#010a04;border:1px solid #0d2b18;border-radius:6px;color:var(--pri)}}
/* chart-grid placeholder  -  used for all image placeholders */
.img-ph{{background:repeating-linear-gradient(0deg,transparent,transparent 15px,rgba(0,230,118,.04) 16px),repeating-linear-gradient(90deg,transparent,transparent 15px,rgba(0,230,118,.04) 16px),linear-gradient(160deg,#010a04 0%,#061a0c 100%);position:relative;overflow:hidden;flex-shrink:0}}
.img-ph img{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;display:block;opacity:0;transition:opacity .5s}}
.img-ph img.loaded{{opacity:1}}
.img-ph::after{{content:'';position:absolute;bottom:0;left:0;right:0;height:50%;background:linear-gradient(to top,rgba(1,10,4,.8),transparent);pointer-events:none}}
/* chart-line SVG decoration inside placeholder */
.img-ph-line{{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;opacity:.12}}
.vp-label{{font-size:13px;font-weight:700;color:#c0ddc8;margin-bottom:4px}}
.vp-desc{{font-family:var(--fm);font-size:11px;color:#2a5a38;line-height:1.55}}

/* ── SECTION 3: LATEST ANALYSIS ── */
.analysis-section{{max-width:1280px;margin:0 auto;padding:48px 20px;display:grid;grid-template-columns:1fr 320px;gap:48px;align-items:start}}
.sec-label{{font-family:var(--fm);font-size:10px;font-weight:700;color:var(--pri);text-transform:uppercase;letter-spacing:3px;padding-bottom:12px;border-bottom:1px solid #0d2b18;margin-bottom:24px;display:flex;align-items:center;gap:8px}}
.sec-label::before{{content:'//';color:#1a4a2a}}
.art-card{{display:grid;grid-template-columns:180px 1fr;border:1px solid #0d2b18;background:#030f07;margin-bottom:1px;overflow:hidden;transition:border-color .2s;cursor:pointer}}
.art-card:hover{{border-color:var(--pri);z-index:1;position:relative}}
.art-card-img{{width:180px;height:130px;object-fit:cover;display:block}}
.art-card-body{{padding:16px 20px;display:flex;flex-direction:column;gap:5px}}
.art-card-tag{{font-family:var(--fm);font-size:9px;color:var(--pri);text-transform:uppercase;letter-spacing:2px;font-weight:700}}
.art-card-title{{font-size:15px;font-weight:700;line-height:1.3;color:#c0ddc8;transition:color .2s}}
.art-card:hover .art-card-title{{color:var(--pri)}}
.art-card-desc{{font-size:12px;color:#3a6a48;line-height:1.65;flex:1}}
.art-card-meta{{font-family:var(--fm);font-size:10px;color:#2a5a38;margin-top:3px}}
.art-card-read{{font-family:var(--fm);font-size:10px;font-weight:700;color:var(--pri);margin-top:4px}}

/* sidebar */
.side-label{{font-family:var(--fm);font-size:10px;font-weight:700;color:var(--pri);text-transform:uppercase;letter-spacing:3px;padding-bottom:12px;border-bottom:1px solid #0d2b18;margin-bottom:0}}
.side-label::before{{content:'//';margin-right:8px;color:#1a4a2a}}
.side-item{{padding:14px 0;border-bottom:1px solid #0d2b18;display:grid;grid-template-columns:80px 1fr;gap:12px;align-items:start;cursor:pointer;transition:opacity .2s}}
.side-item:last-child{{border-bottom:none}}
.side-item:hover{{opacity:.75}}
.side-img{{width:80px;height:56px;object-fit:cover;border-radius:1px;display:block}}
.side-title{{font-size:12px;font-weight:600;line-height:1.35;color:#c0ddc8;margin-bottom:4px}}
.side-meta{{font-family:var(--fm);font-size:10px;color:#2a5a38}}

/* sidebar newsletter */
.side-nl{{background:#030f07;border:1px solid #0d2b18;border-left:2px solid var(--pri);padding:20px;margin-top:24px}}
.side-nl h3{{font-size:14px;font-weight:700;color:#c0ddc8;margin-bottom:5px}}
.side-nl p{{font-family:var(--fm);font-size:11px;color:#3a6a48;line-height:1.6;margin-bottom:14px}}
.nl-inp{{width:100%;background:#020d06;border:1px solid #0d2b18;padding:9px 12px;color:#c0ddc8;font-size:13px;outline:none;margin-bottom:8px;border-radius:2px;font-family:'Space Grotesk',sans-serif}}
.nl-inp:focus{{border-color:var(--pri)}}.nl-inp::placeholder{{color:#2a5a38}}
.nl-btn{{width:100%;background:var(--pri);color:#020d06;border:none;padding:10px;font-size:11px;font-weight:700;font-family:var(--fm);cursor:pointer;text-transform:uppercase;letter-spacing:1px;border-radius:2px}}
.nl-btn:hover{{background:var(--pri2)}}

/* ── SECTION 4: MARKET INTELLIGENCE ── */
.mkt-section{{background:#010a04;border-top:1px solid #0d2b18;border-bottom:1px solid #0d2b18;padding:56px 0}}
.mkt-wrap{{max-width:1280px;margin:0 auto;padding:0 20px}}
.mkt-head{{display:flex;align-items:baseline;justify-content:space-between;margin-bottom:32px;flex-wrap:wrap;gap:8px}}
.mkt-title{{font-family:var(--fm);font-size:10px;font-weight:700;color:var(--pri);text-transform:uppercase;letter-spacing:3px}}
.mkt-title::before{{content:'// ';color:#1a4a2a}}
.mkt-source{{font-family:var(--fm);font-size:10px;color:#2a5a38}}
.mkt-grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:1px;background:#0d2b18;margin-bottom:48px}}
.mkt-card{{background:#020d06;padding:24px 20px;display:flex;flex-direction:column;gap:4px}}
.mkt-sym{{font-family:var(--fm);font-size:11px;font-weight:700;color:#2a5a38;text-transform:uppercase;letter-spacing:2px}}
.mkt-coin-name{{font-size:12px;color:#3a6a48;margin-bottom:4px}}
.mkt-price{{font-family:var(--fm);font-size:26px;font-weight:700;color:#c0ddc8;letter-spacing:-0.5px;line-height:1}}
.mkt-change{{font-family:var(--fm);font-size:12px;font-weight:700;margin-top:4px}}
.mkt-change.up{{color:var(--pri)}}
.mkt-change.dn{{color:#ff5252}}
.mkt-bar{{height:3px;background:#0d2b18;border-radius:2px;margin-top:12px;overflow:hidden}}
.mkt-bar-fill{{height:100%;background:var(--pri);border-radius:2px;transition:width .5s ease}}

/* editorial cards under market intel */
.mkt-editorial{{display:grid;grid-template-columns:repeat(3,1fr);gap:1px;background:#0d2b18}}
.mkt-ed-card{{background:#020d06;overflow:hidden;cursor:pointer;display:block;transition:background .2s}}
.mkt-ed-card:hover{{background:#030f07}}
.mkt-ed-img{{width:100%;height:180px;object-fit:cover;display:block;opacity:.85;transition:opacity .3s}}
.mkt-ed-card:hover .mkt-ed-img{{opacity:1}}
.mkt-ed-body{{padding:18px 20px}}
.mkt-ed-tag{{font-family:var(--fm);font-size:9px;font-weight:700;color:var(--pri);text-transform:uppercase;letter-spacing:2px;margin-bottom:8px}}
.mkt-ed-title{{font-size:15px;font-weight:700;line-height:1.3;color:#c0ddc8;margin-bottom:6px;transition:color .2s}}
.mkt-ed-card:hover .mkt-ed-title{{color:var(--pri)}}
.mkt-ed-desc{{font-family:var(--fm);font-size:11px;color:#2a5a38;line-height:1.6}}

/* ── SECTION 5: NEWSLETTER CTA ── */
.nl-section{{background:#010a04;border-top:2px solid var(--pri);padding:72px 20px;text-align:center;position:relative;overflow:hidden}}
.nl-section::before{{content:'';position:absolute;inset:0;background:radial-gradient(ellipse 80% 60% at 50% 0%,rgba(0,230,118,.06),transparent);pointer-events:none}}
.nl-section-inner{{position:relative;max-width:600px;margin:0 auto}}
.nl-kicker{{font-family:var(--fm);font-size:10px;font-weight:700;color:var(--pri);text-transform:uppercase;letter-spacing:3px;margin-bottom:16px}}
.nl-h2{{font-size:clamp(26px,4vw,44px);font-weight:700;color:#e8f5ec;line-height:1.1;margin-bottom:12px;letter-spacing:-0.5px}}
.nl-sub{{font-size:16px;color:#3a6a48;max-width:480px;margin:0 auto 32px;line-height:1.7}}
.nl-form{{display:flex;max-width:460px;margin:0 auto 16px;border:1px solid #0d2b18;overflow:hidden;border-radius:3px}}
.nl-form input{{flex:1;background:rgba(255,255,255,.04);border:none;padding:14px 18px;color:#e8f5ec;font-size:14px;font-family:'Space Grotesk',sans-serif;outline:none;min-width:0}}
.nl-form input::placeholder{{color:#2a5a38}}
.nl-form button{{background:var(--pri);color:#020d06;border:none;padding:14px 24px;font-size:13px;font-weight:700;font-family:var(--fm);cursor:pointer;text-transform:uppercase;letter-spacing:1px;white-space:nowrap}}
.nl-form button:hover{{background:var(--pri2)}}
.nl-fine{{font-family:var(--fm);font-size:10px;color:#1a4a2a}}

/* ── ABOUT STRIP ── */
.about-strip{{background:#020d06;border-top:1px solid #0d2b18;border-bottom:1px solid #0d2b18;padding:48px 20px}}
.about-strip-inner{{max-width:860px;margin:0 auto;display:grid;grid-template-columns:88px 1fr;gap:28px;align-items:start}}
.about-avatar{{width:88px;height:88px;border-radius:50%;background:var(--pri);display:flex;align-items:center;justify-content:center;font-size:28px;font-weight:700;color:#020d06;flex-shrink:0}}
.about-name{{font-size:20px;font-weight:700;color:#e8f5ec;margin-bottom:3px}}
.about-role{{font-family:var(--fm);font-size:11px;color:var(--pri);margin-bottom:12px;font-weight:600;letter-spacing:1px;text-transform:uppercase}}
.about-bio{{font-size:14px;color:#3a6a48;line-height:1.85}}
.about-bio p+p{{margin-top:10px}}
.about-link{{display:inline-flex;align-items:center;gap:6px;margin-top:16px;font-family:var(--fm);font-size:11px;font-weight:700;color:var(--pri);border:1px solid #0d2b18;padding:7px 16px;border-radius:2px;text-transform:uppercase;letter-spacing:1px;transition:border-color .2s}}
.about-link:hover{{border-color:var(--pri)}}

/* ── FOOTER ── */
.foot{{background:#010604;border-top:1px solid #0a1e10;padding:24px 20px}}
.foot-inner{{max-width:1280px;margin:0 auto;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:14px}}
.foot-copy{{font-family:var(--fm);font-size:11px;color:#1a4a2a}}
.foot-links{{display:flex;gap:20px;flex-wrap:wrap}}
.foot-links a{{font-family:var(--fm);font-size:11px;color:#1a4a2a;transition:color .2s}}
.foot-links a:hover{{color:var(--pri)}}

/* ── SKELETON SHIMMER ── */
@keyframes sk-shimmer{{0%{{background-position:200% 0}}to{{background-position:-200% 0}}}}
.sk-card{{pointer-events:none;border:1px solid #0d2b18;background:#030f07;margin-bottom:1px;overflow:hidden;display:grid;grid-template-columns:180px 1fr}}
.sk-img{{width:180px;height:130px;flex-shrink:0;background:linear-gradient(90deg,#050f08 25%,#091a0d 50%,#050f08 75%);background-size:200% 100%;animation:sk-shimmer 1.8s ease-in-out infinite}}
.sk-body{{padding:16px 20px;flex:1;display:flex;flex-direction:column;gap:10px}}
.sk-line{{height:11px;border-radius:2px;background:linear-gradient(90deg,#050f08 25%,#091a0d 50%,#050f08 75%);background-size:200% 100%;animation:sk-shimmer 1.8s ease-in-out infinite}}
.sk-side-card{{display:grid;grid-template-columns:80px 1fr;gap:12px;align-items:start;padding:14px 0;border-bottom:1px solid #0d2b18;pointer-events:none}}
.sk-side-card:last-child{{border-bottom:none}}
.sk-side-img{{width:80px;height:56px;border-radius:1px;background:linear-gradient(90deg,#050f08 25%,#091a0d 50%,#050f08 75%);background-size:200% 100%;animation:sk-shimmer 1.8s ease-in-out infinite;flex-shrink:0}}
/* section scroll offset for sticky nav */
#analysis,#market,#topics{{scroll-margin-top:60px}}

/* ── REVEAL ON SCROLL ── */
.reveal{{opacity:0;transform:translateY(18px);transition:opacity .55s ease,transform .55s ease}}
.reveal.visible{{opacity:1;transform:none}}

/* ── RESPONSIVE ── */
@media(max-width:1024px){{
  .hero-wrap{{grid-template-columns:1fr 300px}}
  .hero-feat-body{{padding:28px 28px}}
  .hero-h1{{font-size:clamp(20px,3vw,34px)}}
  .analysis-section{{grid-template-columns:1fr;gap:40px}}
  .mkt-grid{{grid-template-columns:repeat(2,1fr)}}
  .mkt-editorial{{grid-template-columns:repeat(2,1fr)}}
}}
@media(max-width:768px){{
  .hero-wrap{{grid-template-columns:1fr}}
  .hero-feat-img{{min-height:360px}}
  .hero-feat-body{{padding:24px 20px}}
  .hero-sub-col{{border-left:none;border-top:1px solid #0d2b18;flex-direction:row;overflow-x:auto;-webkit-overflow-scrolling:touch}}
  .sub-story{{min-width:260px;border-bottom:none;border-right:1px solid #0d2b18;flex:0 0 auto}}
  .sub-story:last-child{{border-right:none}}
  .vp-wrap{{grid-template-columns:repeat(2,1fr)}}
  .vp-item{{border-right:none;border-bottom:1px solid #0d2b18}}
  .vp-item:nth-child(odd){{border-right:1px solid #0d2b18}}
  .nav-links,.nav-right .nav-date,.nav-right .nav-subscribe{{display:none}}
  .nav-burger{{display:flex}}
  .mkt-grid{{grid-template-columns:repeat(2,1fr)}}
  .mkt-editorial{{grid-template-columns:1fr}}
  .about-strip-inner{{grid-template-columns:1fr}}
  .about-avatar{{width:64px;height:64px;font-size:20px}}
  .nl-section{{padding:52px 16px}}
  .art-card{{grid-template-columns:1fr}}
  .art-card-img{{width:100%;height:160px}}
}}
@media(max-width:480px){{
  .vp-wrap{{grid-template-columns:1fr}}
  .vp-item{{border-right:none}}
  .hero-feat-img{{min-height:280px}}
  .hero-h1{{font-size:21px}}
  .hero-feat-body{{padding:20px 16px}}
  .mkt-grid{{grid-template-columns:repeat(2,1fr)}}
  .mkt-price{{font-size:20px}}
  .nl-form{{flex-direction:column;border:none}}
  .nl-form input{{border:1px solid #0d2b18;border-radius:2px}}
  .nl-form button{{border-radius:2px;padding:12px}}
  .foot-inner{{flex-direction:column;text-align:center;gap:12px}}
}}
</style>
</head>
<body>

<!-- ── LIVE TICKER ── -->
<div class="tk-bar">
  <div class="tk-label"><div class="tk-dot"></div>LIVE</div>
  <div class="tk-viewport">
    <div class="tk-track">
      <div class="tk-item"><span class="tk-sym">BTC</span><span id="tk-btc">$67,234</span><span class="tk-up" id="tk-btc-ch">▲ 2.31%</span></div>
      <div class="tk-item"><span class="tk-sym">ETH</span><span id="tk-eth">$3,421</span><span class="tk-dn" id="tk-eth-ch">▼ 0.84%</span></div>
      <div class="tk-item"><span class="tk-sym">SOL</span><span id="tk-sol">$142.50</span><span class="tk-up" id="tk-sol-ch">▲ 4.12%</span></div>
      <div class="tk-item"><span class="tk-sym">BNB</span><span id="tk-bnb">$612</span><span class="tk-up" id="tk-bnb-ch">▲ 1.05%</span></div>
      <div class="tk-item"><span class="tk-sym">FEAR/GREED</span><span class="tk-up" id="tk-fg">72 · Greed</span></div>
      <div class="tk-item"><span class="tk-sym">BTC DOM</span><span id="tk-dom">54.2%</span></div>
      <div class="tk-item"><span class="tk-sym">GLOBAL CAP</span><span id="tk-mcap">$2.41T</span></div>
      <div class="tk-item"><span class="tk-sym">24H VOL</span><span>$98.4B</span></div>
      <div class="tk-item"><span class="tk-sym">BTC</span><span id="tk-btc2">$67,234</span><span class="tk-up" id="tk-btc-ch2">▲ 2.31%</span></div>
      <div class="tk-item"><span class="tk-sym">ETH</span><span id="tk-eth2">$3,421</span><span class="tk-dn" id="tk-eth-ch2">▼ 0.84%</span></div>
      <div class="tk-item"><span class="tk-sym">SOL</span><span id="tk-sol2">$142.50</span><span class="tk-up" id="tk-sol-ch2">▲ 4.12%</span></div>
      <div class="tk-item"><span class="tk-sym">BNB</span><span id="tk-bnb2">$612</span><span class="tk-up" id="tk-bnb-ch2">▲ 1.05%</span></div>
      <div class="tk-item"><span class="tk-sym">FEAR/GREED</span><span class="tk-up" id="tk-fg2">72 · Greed</span></div>
      <div class="tk-item"><span class="tk-sym">BTC DOM</span><span id="tk-dom2">54.2%</span></div>
      <div class="tk-item"><span class="tk-sym">GLOBAL CAP</span><span id="tk-mcap2">$2.41T</span></div>
      <div class="tk-item"><span class="tk-sym">24H VOL</span><span>$98.4B</span></div>
    </div>
  </div>
</div>

<!-- ── NAV ── -->
<nav class="nav" style="position:relative">
  <div class="nav-inner">
    <a href="./" class="nav-logo">{s['name']}<span>{s['tagline']}</span></a>
    <div class="nav-links" id="nav-links-d">
      <a href="#" onclick="window.scrollTo({{top:0,behavior:'smooth'}});return false" class="active">Latest</a>
      <a href="#analysis">Analysis</a>
      <a href="#topics">On-Chain</a>
      <a href="#market">Algo Signals</a>
      <a href="about.html">About</a>
    </div>
    <div class="nav-right">
      <div class="nav-date" id="nav-date"></div>
      <a href="#newsletter" class="nav-subscribe">Subscribe</a>
      <button class="nav-burger" onclick="document.getElementById('nav-mobile').classList.toggle('open')" aria-label="Menu">
        <span></span><span></span><span></span>
      </button>
    </div>
  </div>
  <div class="nav-mobile" id="nav-mobile">
    <a href="#analysis" onclick="document.getElementById('nav-mobile').classList.remove('open')">Latest Analysis</a>
    <a href="#topics" onclick="document.getElementById('nav-mobile').classList.remove('open')">On-Chain Signals</a>
    <a href="#market" onclick="document.getElementById('nav-mobile').classList.remove('open')">Algo Breakdowns</a>
    <a href="about.html">About</a>
    <a href="#newsletter" onclick="document.getElementById('nav-mobile').classList.remove('open')">Subscribe Free</a>
  </div>
</nav>

<!-- ── SECTION 1: HERO GRID ── -->
<section class="hero-section">
  <div class="hero-wrap">
    <a href="./" class="hero-feat" id="hero-feat-link">
      <img id="pxl-img" class="hero-feat-img" src="https://picsum.photos/seed/{seed}/1200/600" alt="{s['name']} hero">
      <div class="hero-feat-ovl"></div>
      <div class="hero-feat-body">
        <div class="hero-badge">Breaking</div>
        <h1 class="hero-h1" id="hero-title">{s['tagline']}</h1>
        <p class="hero-desc" id="hero-desc">{s['hero_sub']}</p>
        <div style="display:flex;align-items:center;gap:14px;flex-wrap:wrap">
          <div class="hero-byline" id="hero-byline"><span>By {s['author']}</span><span id="hero-date-d"></span></div>
          <a class="hero-cta" id="hero-cta" href="#analysis">Read Analysis →</a>
        </div>
      </div>
    </a>
    <div class="hero-sub-col" id="sub-col">
      <a href="#analysis" class="sub-story" id="sub-link-0"><div class="sub-story-img img-ph" id="si-0"><img id="si-img-0" alt=""><div class="img-ph-line"><svg viewBox="0 0 110 60" width="110" height="60" fill="none" stroke="#00e676" stroke-width="1.5"><polyline points="0,50 18,35 36,42 55,18 72,28 90,10 110,16"/></svg></div></div><div class="sub-story-body"><div class="sub-badge">{s['category']}</div><div class="sub-title" id="si-ttl-0">How On-Chain Data Predicted the Last Three Major Market Moves</div><div class="sub-date" id="si-dt-0">Analysis</div></div></a>
      <a href="#analysis" class="sub-story" id="sub-link-1"><div class="sub-story-img img-ph" id="si-1"><img id="si-img-1" alt=""><div class="img-ph-line"><svg viewBox="0 0 110 60" width="110" height="60" fill="none" stroke="#00e676" stroke-width="1.5"><polyline points="0,40 20,55 38,30 55,45 72,20 88,32 110,15"/></svg></div></div><div class="sub-story-body"><div class="sub-badge">Algo Trading</div><div class="sub-title" id="si-ttl-1">Inside a Systematic BTC Strategy: Build, Backtest, Deploy</div><div class="sub-date" id="si-dt-1">Deep Dive</div></div></a>
      <a href="#analysis" class="sub-story" id="sub-link-2"><div class="sub-story-img img-ph" id="si-2"><img id="si-img-2" alt=""><div class="img-ph-line"><svg viewBox="0 0 110 60" width="110" height="60" fill="none" stroke="#00e676" stroke-width="1.5"><polyline points="0,30 15,48 32,22 50,38 68,12 85,24 110,8"/></svg></div></div><div class="sub-story-body"><div class="sub-badge">On-Chain</div><div class="sub-title" id="si-ttl-2">Exchange Outflows Hit 6-Month High  -  What Whale Wallets Are Doing</div><div class="sub-date" id="si-dt-2">Signal Watch</div></div></a>
    </div>
  </div>
</section>

<!-- ── SECTION 2: VALUE PROPS ── -->
<section class="vp-section reveal">
  <div class="vp-wrap">
    <div class="vp-item">
      <div class="vp-icon">{ico_signal}</div>
      <div><div class="vp-label">Live Market Data</div><div class="vp-desc">Real-time prices from CoinGecko, refreshed every 90 seconds directly in your browser</div></div>
    </div>
    <div class="vp-item">
      <div class="vp-icon">{ico_chain}</div>
      <div><div class="vp-label">On-Chain Intelligence</div><div class="vp-desc">Whale moves, exchange inflows, miner behavior, and mempool signals decoded into plain language</div></div>
    </div>
    <div class="vp-item">
      <div class="vp-icon">{ico_gear}</div>
      <div><div class="vp-label">Algo Trade Breakdowns</div><div class="vp-desc">How systematic strategies are built, tested, deployed, and eventually retired  -  the full lifecycle</div></div>
    </div>
    <div class="vp-item">
      <div class="vp-icon">{ico_cross}</div>
      <div><div class="vp-label">No Hype, No Calls</div><div class="vp-desc">Written by a quant trader, not a marketing team. No price predictions, no affiliate deals</div></div>
    </div>
  </div>
</section>

<!-- ── SECTION 3: LATEST ANALYSIS ── -->
<div class="analysis-section" id="analysis">
  <main>
    <div class="sec-label">Latest Analysis</div>
    <div id="main-feed">
      <div class="sk-card"><div class="sk-img"></div><div class="sk-body"><div class="sk-line" style="width:52%;height:9px"></div><div class="sk-line" style="width:88%"></div><div class="sk-line" style="width:74%"></div><div class="sk-line" style="width:45%;height:9px;margin-top:4px"></div></div></div>
      <div class="sk-card"><div class="sk-img"></div><div class="sk-body"><div class="sk-line" style="width:40%;height:9px"></div><div class="sk-line" style="width:92%"></div><div class="sk-line" style="width:68%"></div><div class="sk-line" style="width:38%;height:9px;margin-top:4px"></div></div></div>
      <div class="sk-card"><div class="sk-img"></div><div class="sk-body"><div class="sk-line" style="width:60%;height:9px"></div><div class="sk-line" style="width:80%"></div><div class="sk-line" style="width:55%"></div><div class="sk-line" style="width:50%;height:9px;margin-top:4px"></div></div></div>
    </div>
  </main>
  <aside>
    <div class="side-label">Trending</div>
    <div id="side-feed">
      <div class="sk-side-card"><div class="sk-side-img"></div><div style="flex:1;display:flex;flex-direction:column;gap:8px"><div class="sk-line" style="width:90%"></div><div class="sk-line" style="width:55%;height:9px"></div></div></div>
      <div class="sk-side-card"><div class="sk-side-img"></div><div style="flex:1;display:flex;flex-direction:column;gap:8px"><div class="sk-line" style="width:78%"></div><div class="sk-line" style="width:45%;height:9px"></div></div></div>
      <div class="sk-side-card"><div class="sk-side-img"></div><div style="flex:1;display:flex;flex-direction:column;gap:8px"><div class="sk-line" style="width:85%"></div><div class="sk-line" style="width:60%;height:9px"></div></div></div>
    </div>
    <div class="side-nl">
      <h3>{s['nl_head']}</h3>
      <p>{s['nl_sub']}</p>
      <form id="nl-side" onsubmit="nlSub('nl-side',event)">
        <input type="email" class="nl-inp" placeholder="your@email.com" required>
        <button type="submit" class="nl-btn">Subscribe</button>
      </form>
    </div>
  </aside>
</div>

<!-- ── SECTION 4: MARKET INTELLIGENCE ── -->
<section class="mkt-section" id="market">
  <div class="mkt-wrap">
    <div class="mkt-head">
      <div class="mkt-title">Markets at a Glance <span style="display:inline-flex;align-items:center;gap:5px;margin-left:10px;font-size:9px;color:#3a6a48;font-weight:400;letter-spacing:.5px"><span style="width:7px;height:7px;border-radius:50%;background:var(--pri);display:inline-block;animation:blink 1.2s ease-in-out infinite"></span>LIVE</span></div>
      <div class="mkt-source">CoinGecko API · refreshes every 90s</div>
    </div>
    <div class="mkt-grid">
      <div class="mkt-card">
        <div class="mkt-sym">BTC</div>
        <div class="mkt-coin-name">Bitcoin</div>
        <div class="mkt-price" id="mkt-btc">$67,234</div>
        <div class="mkt-change up" id="mkt-btc-ch">▲ 2.31%</div>
        <div class="mkt-bar"><div class="mkt-bar-fill" id="mkt-btc-bar" style="width:62%"></div></div>
      </div>
      <div class="mkt-card">
        <div class="mkt-sym">ETH</div>
        <div class="mkt-coin-name">Ethereum</div>
        <div class="mkt-price" id="mkt-eth">$3,421</div>
        <div class="mkt-change dn" id="mkt-eth-ch">▼ 0.84%</div>
        <div class="mkt-bar"><div class="mkt-bar-fill" id="mkt-eth-bar" style="width:48%"></div></div>
      </div>
      <div class="mkt-card">
        <div class="mkt-sym">SOL</div>
        <div class="mkt-coin-name">Solana</div>
        <div class="mkt-price" id="mkt-sol">$142.50</div>
        <div class="mkt-change up" id="mkt-sol-ch">▲ 4.12%</div>
        <div class="mkt-bar"><div class="mkt-bar-fill" id="mkt-sol-bar" style="width:38%"></div></div>
      </div>
      <div class="mkt-card">
        <div class="mkt-sym">BNB</div>
        <div class="mkt-coin-name">BNB Chain</div>
        <div class="mkt-price" id="mkt-bnb">$612</div>
        <div class="mkt-change up" id="mkt-bnb-ch">▲ 1.05%</div>
        <div class="mkt-bar"><div class="mkt-bar-fill" id="mkt-bnb-bar" style="width:29%"></div></div>
      </div>
    </div>
    <div class="mkt-editorial" id="mkt-editorial">
      <a class="mkt-ed-card" href="#analysis" id="mkt-ed-1">
        <div class="mkt-ed-img img-ph" style="height:180px"><img id="mei-0" alt="On-Chain Analysis"><div class="img-ph-line"><svg viewBox="0 0 300 180" width="300" height="180" fill="none" stroke="#00e676" stroke-width="1.5"><polyline points="0,140 40,100 80,120 130,55 180,75 230,30 280,50 300,40"/><polyline points="0,160 40,145 80,155 130,100 180,120 230,75 280,90 300,80" stroke-width="0.6"/></svg></div></div>
        <div class="mkt-ed-body"><div class="mkt-ed-tag">On-Chain</div><div class="mkt-ed-title">Reading Blockchain Data for Trade Signals</div><div class="mkt-ed-desc">Exchange inflows, whale accumulation patterns, and what they historically precede.</div></div>
      </a>
      <a class="mkt-ed-card" href="#analysis" id="mkt-ed-2">
        <div class="mkt-ed-img img-ph" style="height:180px"><img id="mei-1" alt="Algo Strategy"><div class="img-ph-line"><svg viewBox="0 0 300 180" width="300" height="180" fill="none" stroke="#00e676" stroke-width="1.5"><polyline points="0,100 50,130 90,80 140,110 190,45 240,65 280,30 300,20"/></svg></div></div>
        <div class="mkt-ed-body"><div class="mkt-ed-tag">Algo Trading</div><div class="mkt-ed-title">How Systematic Strategies Degrade Over Time</div><div class="mkt-ed-desc">Every edge has a shelf life. Knowing when to retire a strategy is harder than building it.</div></div>
      </a>
      <a class="mkt-ed-card" href="#analysis" id="mkt-ed-3">
        <div class="mkt-ed-img img-ph" style="height:180px"><img id="mei-2" alt="Market Structure"><div class="img-ph-line"><svg viewBox="0 0 300 180" width="300" height="180" fill="none" stroke="#00e676" stroke-width="1.5"><polyline points="0,120 35,90 70,105 110,60 155,80 200,35 245,55 300,25"/></svg></div></div>
        <div class="mkt-ed-body"><div class="mkt-ed-tag">Market Structure</div><div class="mkt-ed-title">Crypto Market Microstructure for Retail Traders</div><div class="mkt-ed-desc">Order books, liquidity gaps, and why price moves the way it does at key levels.</div></div>
      </a>
    </div>
  </div>
</section>

<!-- ── SECTION 5: DEEP DIVE TOPICS ── -->
<section id="topics" style="background:#010a04;border-top:1px solid #0d2b18;padding:56px 0">
  <div class="mkt-wrap">
    <div class="mkt-head">
      <div class="mkt-title">Deep Dive Topics</div>
    </div>
    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:1px;background:#0d2b18" id="topics-grid">
      <a class="mkt-ed-card" href="#analysis" id="td-0">
        <div class="mkt-ed-img img-ph" style="height:200px"><img id="td-img-0" alt="Bitcoin Analysis"><div class="img-ph-line"><svg viewBox="0 0 300 200" width="300" height="200" fill="none" stroke="#00e676" stroke-width="1.5"><polyline points="0,160 50,120 100,140 150,70 200,90 250,40 300,50"/></svg></div></div>
        <div class="mkt-ed-body"><div class="mkt-ed-tag">On-Chain Analysis</div><div class="mkt-ed-title" id="td-ttl-0">Bitcoin On-Chain Intelligence</div><div class="mkt-ed-desc">Exchange inflows, whale accumulation, UTXO age bands, and what they signal about cycle positioning.</div></div>
      </a>
      <a class="mkt-ed-card" href="#analysis" id="td-1">
        <div class="mkt-ed-img img-ph" style="height:200px"><img id="td-img-1" alt="Algo Trading"><div class="img-ph-line"><svg viewBox="0 0 300 200" width="300" height="200" fill="none" stroke="#00e676" stroke-width="1.5"><polyline points="0,130 50,160 100,90 150,120 200,55 250,75 300,30"/></svg></div></div>
        <div class="mkt-ed-body"><div class="mkt-ed-tag">Algo Trading</div><div class="mkt-ed-title" id="td-ttl-1">Systematic Strategy Breakdowns</div><div class="mkt-ed-desc">How quant strategies are built, tested under real market conditions, and retired when the edge degrades.</div></div>
      </a>
      <a class="mkt-ed-card" href="#analysis" id="td-2">
        <div class="mkt-ed-img img-ph" style="height:200px"><img id="td-img-2" alt="Market Structure"><div class="img-ph-line"><svg viewBox="0 0 300 200" width="300" height="200" fill="none" stroke="#00e676" stroke-width="1.5"><polyline points="0,100 40,80 90,110 140,50 190,70 240,25 300,35"/></svg></div></div>
        <div class="mkt-ed-body"><div class="mkt-ed-tag">Market Structure</div><div class="mkt-ed-title" id="td-ttl-2">Crypto Microstructure for Retail</div><div class="mkt-ed-desc">Order books, liquidity voids, liquidation cascades, and why price behaves the way it does at key levels.</div></div>
      </a>
    </div>
  </div>
</section>

<!-- ── SECTION 6: NEWSLETTER ── -->
<section class="nl-section" id="newsletter">
  <div class="nl-section-inner">
    <div class="nl-kicker">Free Weekly Intelligence Report</div>
    <h2 class="nl-h2">{s['nl_head']}</h2>
    <p class="nl-sub">{s['nl_sub']}</p>
    <form class="nl-form" id="nl-main" onsubmit="nlSub('nl-main',event)">
      <input type="email" placeholder="your@email.com" required>
      <button type="submit">Subscribe Free →</button>
    </form>
    <div class="nl-fine">No spam. Unsubscribe anytime. Written by a quant, not a bot.</div>
  </div>
</section>

<!-- ── ABOUT STRIP ── -->
<section class="about-strip">
  <div class="about-strip-inner">
    <div class="about-avatar">{ini}</div>
    <div>
      <div class="about-name">{s['author']}</div>
      <div class="about-role">{s['author_title']}</div>
      <div class="about-bio"><p>{s['bio1']}</p><p>{s['bio2']}</p></div>
      <a href="about.html" class="about-link">Full bio &amp; methodology →</a>
    </div>
  </div>
</section>

<!-- ── FOOTER ── -->
<footer class="foot">
  <div class="foot-inner">
    <span class="foot-copy">© {s['name']} · {s['footer_desc']}</span>
    <div class="foot-links">
      <a href="./">Home</a>
      <a href="about.html">About</a>
      <a href="privacy.html">Privacy</a>
      <a href="terms.html">Terms</a>
      <a href="sms.html">SMS</a>
    </div>
  </div>
</footer>

<script>
document.getElementById('nav-date').textContent=new Date().toLocaleDateString('en-US',{{weekday:'short',month:'short',day:'numeric'}});
document.getElementById('hero-date-d').textContent=new Date().toLocaleDateString('en-US',{{month:'long',day:'numeric',year:'numeric'}});

/* ── live CoinGecko ticker + market cards ── */
(async function(){{
  var p={{btc:67234,eth:3421,sol:142.5,bnb:612}};
  var c={{btc:2.31,eth:-0.84,sol:4.12,bnb:1.05}};
  function fmt(v){{return v>=1000?'$'+v.toFixed(0).replace(/\\B(?=(\\d{{3}})+(?!\\d))/g,','):'$'+v.toFixed(2);}}
  function updTk(){{
    ['btc','eth','sol','bnb'].forEach(function(k){{
      var up=c[k]>=0;
      var pv=fmt(p[k]),cv=(up?'▲ ':'▼ ')+Math.abs(c[k]).toFixed(2)+'%',cls=up?'tk-up':'tk-dn';
      ['','2'].forEach(function(s){{
        var pe=document.getElementById('tk-'+k+s),ce=document.getElementById('tk-'+k+'-ch'+s);
        if(pe)pe.textContent=pv;if(ce){{ce.textContent=cv;ce.className=cls;}}
      }});
      /* market cards */
      var mp=document.getElementById('mkt-'+k),mc=document.getElementById('mkt-'+k+'-ch');
      if(mp)mp.textContent=pv;
      if(mc){{mc.textContent=cv;mc.className='mkt-change '+(up?'up':'dn');}}
    }});
  }}
  function fetchPrices(){{
    return fetch('https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,solana,binancecoin&vs_currencies=usd&include_24hr_change=true',{{cache:'no-store'}})
      .then(function(r){{return r.json();}}).then(function(d){{
        if(d.bitcoin){{p.btc=d.bitcoin.usd;c.btc=d.bitcoin.usd_24h_change||0;}}
        if(d.ethereum){{p.eth=d.ethereum.usd;c.eth=d.ethereum.usd_24h_change||0;}}
        if(d.solana){{p.sol=d.solana.usd;c.sol=d.solana.usd_24h_change||0;}}
        if(d.binancecoin){{p.bnb=d.binancecoin.usd;c.bnb=d.binancecoin.usd_24h_change||0;}}
        updTk();
      }}).catch(function(){{updTk();}});
  }}
  fetchPrices();
  setInterval(function(){{['btc','eth','sol','bnb'].forEach(function(k){{p[k]*=(1+(Math.random()-.5)*.0006);}});updTk();}},4000);
  setInterval(fetchPrices,90000);
}})();

/* ── helper: load img into .img-ph wrapper ── */
function setPhImg(wrapperId,src,alt){{
  var w=document.getElementById(wrapperId);if(!w||!src)return;
  var i=w.querySelector('img');
  if(!i){{i=document.createElement('img');w.appendChild(i);}}
  i.alt=alt||'';
  i.onload=function(){{i.classList.add('loaded');}};
  i.src=src;
}}
/* ── Pexels multi-image loader ── */
(function(){{
  var k=localStorage.getItem('pexelsKey');if(!k)return;
  fetch('https://api.pexels.com/v1/search?query={q}&per_page=12&orientation=landscape',{{headers:{{Authorization:k}}}})
    .then(function(r){{return r.json();}}).then(function(d){{
      if(!d.photos||!d.photos.length)return;
      var ph=d.photos;
      // hero already handled by _pexels_js (pxl-img)
      // sub-stories
      ['si-0','si-1','si-2'].forEach(function(id,i){{
        if(ph[i+1])setPhImg(id,ph[i+1].src.medium,ph[i+1].alt||'');
      }});
      // market editorial cards
      ['mkt-ed-1','mkt-ed-2','mkt-ed-3'].forEach(function(id,i){{
        var el=document.getElementById(id);if(!el)return;
        var ph2=el.querySelector('.img-ph');if(!ph2)return;
        var img=ph2.querySelector('img');if(img&&ph[i+4]){{img.alt=ph[i+4].alt||'';img.onload=function(){{img.classList.add('loaded');}};img.src=ph[i+4].src.large;}}
      }});
    }}).catch(function(){{}});
}})();
/* ── articles.json loader ── */
async function loadPosts(){{
  try{{
    var r=await fetch('./articles.json');if(!r.ok)throw 0;
    var posts=await r.json();if(!posts||!posts.length)throw 0;
    /* hero  -  post[0] */
    var h0=posts[0];
    var hi=document.getElementById('pxl-img');
    if(hi&&h0.image){{hi.onload=function(){{hi.style.opacity='1';}};hi.src=h0.image;}}
    var ht=document.getElementById('hero-title'),hd=document.getElementById('hero-desc'),hl=document.getElementById('hero-feat-link'),hb=document.getElementById('hero-byline');
    if(ht)ht.textContent=h0.title;
    if(hd)hd.textContent=h0.meta_description||'';
    if(hl)hl.href='./'+h0.slug+'/';
    if(hb)hb.innerHTML='<span>By '+(h0.author||'{s['author']}')+'</span><span>'+(h0.date_iso||'')+'</span>';
    /* sub-stories  -  posts[1..3] */
    if(posts.length>1){{
      posts.slice(1,4).forEach(function(p,i){{
        var ttl=document.getElementById('si-ttl-'+i),dt=document.getElementById('si-dt-'+i),w=document.getElementById('si-'+i);
        if(ttl)ttl.textContent=p.title;
        if(dt)dt.textContent=p.date_iso||'';
        var sl=document.getElementById('sub-link-'+i);if(sl)sl.href='./'+p.slug+'/';
        if(p.image&&w)setPhImg('si-'+i,p.image,p.title);
      }});
    }}
    /* main feed  -  posts[1..end] (all articles below hero) */
    var mf=document.getElementById('main-feed');
    if(mf&&posts.length>1){{mf.innerHTML=posts.slice(1).map(function(p){{
      var imgHtml=p.image
        ?'<img class="art-card-img" src="'+p.image+'" alt="'+p.title+'" loading="lazy" style="width:180px;height:130px;object-fit:cover;flex-shrink:0;display:block">'
        :'<div class="art-card-img img-ph" style="height:130px;flex-shrink:0"><div class="img-ph-line"><svg viewBox="0 0 180 130" width="180" height="130" fill="none" stroke="#00e676" stroke-width="1.5"><polyline points="0,100 30,70 60,85 90,40 120,55 150,20 180,30"/></svg></div></div>';
      return '<a href="./'+p.slug+'/" style="display:block"><div class="art-card">'+imgHtml+'<div class="art-card-body"><div class="art-card-tag">{s['category']}</div><div class="art-card-title">'+p.title+'</div><div class="art-card-desc">'+(p.meta_description||'').slice(0,110)+'</div><div class="art-card-meta">'+(p.date_iso||'')+(p.author?' · '+p.author:'')+'</div></div></div></a>';
    }}).join('');}}
    /* sidebar trending  -  posts[1..5] */
    var sf=document.getElementById('side-feed');
    if(sf){{sf.innerHTML=posts.slice(1,6).map(function(p){{
      var imgHtml=p.image
        ?'<img class="side-img" src="'+p.image+'" alt="'+p.title+'" loading="lazy" style="width:80px;height:56px;object-fit:cover;flex-shrink:0;border-radius:1px">'
        :'<div class="side-img img-ph" style="height:56px"></div>';
      return '<a href="./'+p.slug+'/" style="display:block"><div class="side-item">'+imgHtml+'<div><div class="side-title">'+p.title+'</div><div class="side-meta">'+(p.date_iso||'')+'</div></div></div></a>';
    }}).join('');}}
    /* market editorial cards  -  top 3 articles */
    [[posts[0],'mkt-ed-1','{s['category']}'],[posts[1],'mkt-ed-2','Algo Trading'],[posts[2],'mkt-ed-3','Market Structure']].forEach(function(row){{
      var p=row[0],id=row[1],tag=row[2];
      if(!p)return;
      var el=document.getElementById(id);if(!el)return;
      el.href='./'+p.slug+'/';
      var ph=el.querySelector('.img-ph');
      if(ph&&p.image){{var i=ph.querySelector('img');if(i){{i.alt=p.title;i.onload=function(){{i.classList.add('loaded');}};i.src=p.image;}}}}
      var body=el.querySelector('.mkt-ed-body');
      if(body)body.innerHTML='<div class="mkt-ed-tag">'+tag+'</div><div class="mkt-ed-title">'+p.title+'</div><div class="mkt-ed-desc">'+(p.meta_description||'').slice(0,100)+'</div>';
    }});
    /* deep dive topic cards  -  wire images + links */
    posts.slice(0,3).forEach(function(p,i){{
      var el=document.getElementById('td-'+i);if(!el)return;
      el.href='./'+p.slug+'/';
      var ttl=document.getElementById('td-ttl-'+i);if(ttl)ttl.textContent=p.title;
      if(p.image){{var img=document.getElementById('td-img-'+i);if(img){{img.alt=p.title;img.onload=function(){{img.classList.add('loaded');}};img.src=p.image;}}}}
    }});
  }}catch(e){{/* placeholders stay */}}
}}

function nlSub(id,e){{
  e.preventDefault();
  var f=document.getElementById(id);
  if(f)f.innerHTML='<p style="color:var(--pri);font-family:var(--fm);font-size:13px;font-weight:700;padding:10px 0">You\'re on the list. Welcome.</p>';
}}

/* ── reveal on scroll ── */
(function(){{
  var els=document.querySelectorAll('.reveal');
  if(!els.length)return;
  var io=new IntersectionObserver(function(entries){{
    entries.forEach(function(e){{if(e.isIntersecting){{e.target.classList.add('visible');io.unobserve(e.target);}}}});
  }},{{threshold:0.08}});
  els.forEach(function(el){{io.observe(el);}});
}})();

/* ── active nav highlight on scroll ── */
(function(){{
  var sections=['analysis','market','topics','newsletter'];
  var links=document.querySelectorAll('.nav-links a');
  var map={{'analysis':1,'market':3,'topics':2,'newsletter':4}};
  function onScroll(){{
    var scrollY=window.pageYOffset+80;
    var current='';
    sections.forEach(function(id){{
      var el=document.getElementById(id);
      if(el&&el.offsetTop<=scrollY)current=id;
    }});
    links.forEach(function(a,i){{
      a.classList.toggle('active',current&&map[current]===i);
    }});
    if(!current)links[0].classList.add('active');
  }}
  window.addEventListener('scroll',onScroll,{{passive:true}});
}})();

loadPosts();
{pxjs}
</script>
</body></html>"""


def terminal_about(s):
    cv   = css_vars(s)
    ini  = ''.join(w[0].upper() for w in s['author'].split()[:2])
    story = _story_html(s, 'abt-p')
    pxjs  = _pexels_js(s)
    seed  = abs(hash(s['id'])) % 1000
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>About {s['author']} · {s['name']}</title>
<meta name="description" content="{s['footer_desc']}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Space+Mono:wght@400;700&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
:root{{{cv}--fh:'Space Grotesk',system-ui,sans-serif;--fm:'Space Mono',monospace;}}
body{{background:#050908;color:#c0ddc8;font-family:'Space Grotesk',system-ui,sans-serif;font-size:15px;line-height:1.7;min-height:100vh;overflow-x:hidden}}
a{{color:var(--pri);text-decoration:none}}

/* TICKER */
.tk-bar{{background:#020d06;border-bottom:1px solid #0d2b18;height:36px;display:flex;align-items:center;overflow:hidden}}
.tk-label{{font-family:var(--fm);font-size:9px;font-weight:700;color:#020d06;background:var(--pri);padding:0 14px;height:100%;display:flex;align-items:center;flex-shrink:0;letter-spacing:2px;text-transform:uppercase}}
.tk-vp{{flex:1;overflow:hidden}}
.tk-tr{{display:flex;white-space:nowrap;animation:ticker-scroll 40s linear infinite}}
@keyframes ticker-scroll{{from{{transform:translateX(0)}}to{{transform:translateX(-50%)}}}}
.tk-it{{font-family:var(--fm);font-size:11px;color:#4a7a5a;display:inline-flex;gap:7px;align-items:center;padding:0 22px;border-right:1px solid #0d2b18}}
.tk-sy{{color:#a0cfb0;font-weight:700}}
.tk-up{{color:var(--pri);font-weight:700}}
.tk-dn{{color:#ff5252;font-weight:700}}
/* NAV */
.nav{{background:#020d06;border-bottom:1px solid #0d2b18;position:sticky;top:0;z-index:99}}
.nav-in{{max-width:1280px;margin:0 auto;padding:0 20px;display:flex;align-items:center;height:58px;gap:0}}
.nav-logo{{font-size:20px;font-weight:700;color:var(--pri);margin-right:40px;flex-shrink:0;letter-spacing:-0.5px;text-decoration:none}}
.nav-logo span{{font-family:var(--fm);font-size:10px;color:#2a5a38;font-weight:400;margin-left:6px;letter-spacing:1px;text-transform:uppercase}}
.nav-links{{display:flex;gap:0;height:100%;flex:1}}
.nav-links a{{font-family:var(--fm);font-size:11px;font-weight:700;color:#3a6a48;text-transform:uppercase;letter-spacing:1px;padding:0 14px;height:100%;display:flex;align-items:center;border-bottom:2px solid transparent;transition:all .2s;margin-bottom:-1px;text-decoration:none}}
.nav-links a:hover,.nav-links a.active{{color:var(--pri);border-bottom-color:var(--pri)}}
.nav-right{{display:flex;align-items:center;gap:14px;flex-shrink:0;margin-left:auto}}
.nav-date-abt{{font-family:var(--fm);font-size:10px;color:#2a5a38}}
.nav-subscribe{{font-family:var(--fm);font-size:10px;font-weight:700;color:#020d06;background:var(--pri);padding:6px 14px;border-radius:2px;text-transform:uppercase;letter-spacing:1px;white-space:nowrap;text-decoration:none}}

/* AUTHOR HERO */
.hero{{background:#010a04;border-bottom:1px solid #0d2b18;padding:0}}
.hero-banner{{width:100%;height:300px;object-fit:cover;display:block;opacity:0;transition:opacity 1s}}
.hero-banner-ph{{width:100%;height:300px;background:#020d06;position:relative;overflow:hidden}}
.hero-banner-ph::after{{content:'';position:absolute;inset:0;background:linear-gradient(135deg,#030f07 0%,#010a04 100%);}}
.hero-content{{max-width:1100px;margin:0 auto;padding:0 20px}}
.hero-card{{background:#020d06;border:1px solid #0d2b18;border-top:none;display:grid;grid-template-columns:auto 1fr auto;gap:28px;align-items:center;padding:28px 32px}}
.hero-avatar{{width:100px;height:100px;border-radius:50%;background:var(--pri);display:flex;align-items:center;justify-content:center;font-size:32px;font-weight:700;color:#020d06;flex-shrink:0;border:3px solid #0d2b18}}
.hero-info-name{{font-size:28px;font-weight:700;color:#e8f5ec;margin-bottom:4px;letter-spacing:-0.5px}}
.hero-info-role{{font-family:var(--fm);font-size:11px;color:var(--pri);text-transform:uppercase;letter-spacing:2px;margin-bottom:14px}}
.hero-info-desc{{font-size:14px;color:#3a6a48;line-height:1.65;max-width:560px}}
.hero-stats{{display:flex;flex-direction:column;gap:14px;flex-shrink:0;border-left:1px solid #0d2b18;padding-left:28px}}
.stat-item{{text-align:right}}
.stat-num{{font-family:var(--fm);font-size:22px;font-weight:700;color:var(--pri);line-height:1}}
.stat-label{{font-family:var(--fm);font-size:9px;color:#2a5a38;text-transform:uppercase;letter-spacing:2px;margin-top:2px}}

/* CONTENT WRAPPER */
.wrap{{max-width:1100px;margin:0 auto;padding:0 20px}}
.two-col{{display:grid;grid-template-columns:1fr 340px;gap:48px;align-items:start;padding:56px 0}}

/* STORY SECTION */
.sec-kicker{{font-family:var(--fm);font-size:10px;font-weight:700;color:var(--pri);text-transform:uppercase;letter-spacing:3px;padding-bottom:12px;border-bottom:1px solid #0d2b18;margin-bottom:24px}}
.sec-kicker::before{{content:'// ';color:#1a4a2a}}
.abt-p{{color:#5a8a6a;font-size:15px;line-height:1.9;margin-bottom:16px}}
.abt-p:last-child{{margin-bottom:0}}

/* EXPERTISE GRID */
.exp-grid{{display:grid;grid-template-columns:1fr 1fr;gap:1px;background:#0d2b18;margin-top:24px}}
.exp-card{{background:#020d06;padding:20px 22px}}
.exp-icon{{font-size:26px;margin-bottom:10px}}
.exp-title{{font-size:14px;font-weight:700;color:#c0ddc8;margin-bottom:5px}}
.exp-desc{{font-family:var(--fm);font-size:11px;color:#2a5a38;line-height:1.6}}

/* METHODOLOGY */
.meth-list{{display:flex;flex-direction:column;gap:0;background:#020d06;border:1px solid #0d2b18;margin-top:24px}}
.meth-item{{display:grid;grid-template-columns:56px 1fr;gap:0;border-bottom:1px solid #0d2b18}}
.meth-item:last-child{{border-bottom:none}}
.meth-num{{font-family:var(--fm);font-size:22px;font-weight:700;color:#0d2b18;padding:20px 0 20px 20px;display:flex;align-items:flex-start}}
.meth-body{{padding:20px 20px 20px 0}}
.meth-title{{font-size:14px;font-weight:700;color:#c0ddc8;margin-bottom:5px}}
.meth-desc{{font-family:var(--fm);font-size:11px;color:#2a5a38;line-height:1.65}}

/* SIDEBAR */
.side-nl{{background:#020d06;border:1px solid #0d2b18;border-left:2px solid var(--pri);padding:24px;margin-bottom:28px}}
.side-nl h3{{font-size:16px;font-weight:700;color:#e8f5ec;margin-bottom:6px}}
.side-nl p{{font-family:var(--fm);font-size:11px;color:#2a5a38;line-height:1.65;margin-bottom:16px}}
.nl-inp{{width:100%;background:#010a04;border:1px solid #0d2b18;padding:10px 12px;color:#c0ddc8;font-size:13px;font-family:'Space Grotesk',sans-serif;outline:none;margin-bottom:9px;border-radius:2px}}
.nl-inp:focus{{border-color:var(--pri)}}.nl-inp::placeholder{{color:#2a5a38}}
.nl-btn{{width:100%;background:var(--pri);color:#020d06;border:none;padding:11px;font-size:12px;font-weight:700;font-family:var(--fm);cursor:pointer;text-transform:uppercase;letter-spacing:1px;border-radius:2px}}
.nl-btn:hover{{background:var(--pri2)}}

/* SITE PILLARS */
.pillar-list{{display:flex;flex-direction:column;gap:1px;background:#0d2b18;border:1px solid #0d2b18;margin-bottom:28px}}
.pillar{{background:#020d06;padding:14px 16px;display:flex;align-items:center;gap:12px}}
.pillar-dot{{width:6px;height:6px;border-radius:50%;background:var(--pri);flex-shrink:0}}
.pillar-text{{font-family:var(--fm);font-size:11px;color:#3a6a48;line-height:1.5}}
.pillar-text strong{{color:#c0ddc8;display:block;margin-bottom:2px;font-size:12px}}

/* RECENT POSTS */
.recent-post{{display:grid;grid-template-columns:80px 1fr;gap:12px;padding:14px 0;border-bottom:1px solid #0d2b18;cursor:pointer;transition:opacity .2s}}
.recent-post:last-child{{border-bottom:none}}
.recent-post:hover{{opacity:.75}}
.recent-img{{width:80px;height:56px;object-fit:cover;border-radius:1px;display:block}}
.recent-title{{font-size:13px;font-weight:600;line-height:1.35;color:#c0ddc8;margin-bottom:4px}}
.recent-meta{{font-family:var(--fm);font-size:10px;color:#2a5a38}}

/* CONTRIBUTORS */
.contrib-grid{{display:grid;grid-template-columns:1fr 1fr;gap:1px;background:#0d2b18;border:1px solid #0d2b18}}
.contrib-card{{background:#020d06;padding:16px 18px;display:flex;align-items:flex-start;gap:12px}}
.contrib-av{{width:40px;height:40px;border-radius:50%;background:var(--pri);display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:700;color:#020d06;flex-shrink:0;font-family:var(--fm)}}
.contrib-name{{font-size:13px;font-weight:700;color:#c0ddc8;margin-bottom:2px}}
.contrib-role{{font-family:var(--fm);font-size:9px;color:var(--pri);text-transform:uppercase;letter-spacing:1.5px;margin-bottom:5px}}
.contrib-bio{{font-family:var(--fm);font-size:10px;color:#2a5a38;line-height:1.6}}

/* COMMENTS */
.comment{{background:#020d06;border:1px solid #0d2b18;border-left:2px solid #0d2b18;padding:16px 18px;margin-bottom:1px;transition:border-left-color .2s}}
.comment:hover{{border-left-color:var(--pri)}}
.comment-text{{font-size:14px;color:#5a8a6a;line-height:1.75;margin-bottom:10px;font-style:italic}}
.comment-author{{font-family:var(--fm);font-size:10px;color:#2a5a38;font-weight:700;text-transform:uppercase;letter-spacing:1.5px}}

/* FOOTER */
.foot{{background:#010604;border-top:1px solid #0a1e10;padding:22px 20px;margin-top:64px}}
.foot-in{{max-width:1100px;margin:0 auto;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px}}
.foot-copy{{font-family:var(--fm);font-size:11px;color:#1a4a2a}}
.foot-links{{display:flex;gap:18px;flex-wrap:wrap}}
.foot-links a{{font-family:var(--fm);font-size:11px;color:#1a4a2a;transition:color .2s}}
.foot-links a:hover{{color:var(--pri)}}

/* RESPONSIVE */
@media(max-width:900px){{
  .two-col{{grid-template-columns:1fr;gap:32px;padding:40px 0}}
  .hero-card{{grid-template-columns:auto 1fr;}}
  .hero-stats{{display:none}}
  .exp-grid{{grid-template-columns:1fr}}
  .contrib-grid{{grid-template-columns:1fr}}
}}
@media(max-width:600px){{
  .hero-banner,.hero-banner-ph{{height:200px}}
  .hero-card{{grid-template-columns:1fr;padding:20px 16px;gap:16px}}
  .hero-avatar{{width:72px;height:72px;font-size:22px}}
  .hero-info-name{{font-size:22px}}
  .nav-in{{padding:0 16px}}
  .nav-links a:not(.active){{display:none}}
  .foot-in{{flex-direction:column;text-align:center}}
}}
</style>
</head>
<body>

<!-- TICKER -->
<div class="tk-bar">
  <div class="tk-label">LIVE</div>
  <div class="tk-vp">
    <div class="tk-tr">
      <div class="tk-it"><span class="tk-sy">BTC</span><span id="abt-btc">$67,234</span><span class="tk-up">▲ 2.31%</span></div>
      <div class="tk-it"><span class="tk-sy">ETH</span><span id="abt-eth">$3,421</span><span class="tk-dn">▼ 0.84%</span></div>
      <div class="tk-it"><span class="tk-sy">SOL</span><span>$142.50</span><span class="tk-up">▲ 4.12%</span></div>
      <div class="tk-it"><span class="tk-sy">BNB</span><span>$612</span><span class="tk-up">▲ 1.05%</span></div>
      <div class="tk-it"><span class="tk-sy">FEAR/GREED</span><span class="tk-up">72 · Greed</span></div>
      <div class="tk-it"><span class="tk-sy">BTC DOM</span><span>54.2%</span></div>
      <div class="tk-it"><span class="tk-sy">BTC</span><span>$67,234</span><span class="tk-up">▲ 2.31%</span></div>
      <div class="tk-it"><span class="tk-sy">ETH</span><span>$3,421</span><span class="tk-dn">▼ 0.84%</span></div>
      <div class="tk-it"><span class="tk-sy">SOL</span><span>$142.50</span><span class="tk-up">▲ 4.12%</span></div>
      <div class="tk-it"><span class="tk-sy">FEAR/GREED</span><span class="tk-up">72 · Greed</span></div>
    </div>
  </div>
</div>
<!-- NAV -->
<nav class="nav">
  <div class="nav-in">
    <a href="./" class="nav-logo">{s['name']}<span>{s['tagline']}</span></a>
    <div class="nav-links">
      <a href="./">Latest</a>
      <a href="./">Analysis</a>
      <a href="./">On-Chain</a>
      <a href="about.html" class="active">About</a>
    </div>
    <div class="nav-right">
      <div class="nav-date-abt" id="abt-nav-date"></div>
      <a href="#subscribe" class="nav-subscribe">Subscribe Free</a>
    </div>
  </div>
</nav>

<!-- AUTHOR HERO -->
<div class="hero">
  <div class="hero-banner-ph" style="position:relative">
    <img id="pxl-img" class="hero-banner" style="position:absolute;inset:0;width:100%;height:100%;object-fit:cover" alt="{s['name']}">
    <div style="position:absolute;inset:0;background:linear-gradient(to bottom,rgba(1,10,4,.3) 0%,rgba(1,10,4,.85) 100%)"></div>
  </div>
  <div class="hero-content">
    <div class="hero-card">
      <div class="hero-avatar">{ini}</div>
      <div>
        <div class="hero-info-name">{s['author']}</div>
        <div class="hero-info-role">{s['author_title']}</div>
        <div class="hero-info-desc">{s['hero_sub']}</div>
      </div>
      <div class="hero-stats">
        <div class="stat-item"><div class="stat-num">8+</div><div class="stat-label">Years trading</div></div>
        <div class="stat-item"><div class="stat-num">$10M+</div><div class="stat-label">Vol managed</div></div>
        <div class="stat-item"><div class="stat-num">Indep.</div><div class="stat-label">No sponsors</div></div>
      </div>
    </div>
  </div>
</div>

<!-- MAIN CONTENT -->
<div class="wrap">
  <div class="two-col">

    <!-- LEFT: story + expertise + methodology + contributors + comments -->
    <div>

      <!-- Background Story -->
      <div class="sec-kicker">Background</div>
      {story}

      <!-- Expertise Grid -->
      <div style="margin-top:48px">
        <div class="sec-kicker">Areas of Expertise</div>
        <div class="exp-grid">
          <div class="exp-card"><div class="exp-icon"><svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg></div><div class="exp-title">On-Chain Analysis</div><div class="exp-desc">Exchange flows, whale wallets, miner behavior, mempool signals  -  reading the blockchain for trade intelligence</div></div>
          <div class="exp-card"><div class="exp-icon"><svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M12 1v3M12 20v3M4.22 4.22l2.12 2.12M17.66 17.66l2.12 2.12M1 12h3M20 12h3M4.22 19.78l2.12-2.12M17.66 6.34l2.12-2.12"/></svg></div><div class="exp-title">Algorithmic Strategy</div><div class="exp-desc">Building, backtesting, deploying, and retiring systematic strategies. The full lifecycle from concept to capital</div></div>
          <div class="exp-card"><div class="exp-icon"><svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg></div><div class="exp-title">Market Microstructure</div><div class="exp-desc">Order book dynamics, liquidity gaps, bid-ask spreads, and how price actually moves at key levels</div></div>
          <div class="exp-card"><div class="exp-icon"><svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="2" width="8" height="8" rx="1"/><rect x="14" y="2" width="8" height="8" rx="1"/><rect x="2" y="14" width="8" height="8" rx="1"/><path d="M14 17h8M18 14v6"/></svg></div><div class="exp-title">Quantitative Methods</div><div class="exp-desc">Statistical analysis, signal validation, walk-forward testing, and the math behind what most traders skip</div></div>
          <div class="exp-card"><div class="exp-icon"><svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg></div><div class="exp-title">Risk Management</div><div class="exp-desc">Position sizing frameworks, drawdown limits, portfolio construction under uncertainty, Kelly criterion in practice</div></div>
          <div class="exp-card"><div class="exp-icon"><svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/><line x1="12" y1="17" x2="12.01" y2="17"/><circle cx="12" cy="12" r="10"/></svg></div><div class="exp-title">Trade Psychology</div><div class="exp-desc">Why most traders fail despite good systems  -  and the behavioral discipline that actually separates performance</div></div>
        </div>
      </div>

      <!-- Methodology -->
      <div style="margin-top:48px">
        <div class="sec-kicker">Research Methodology</div>
        <div class="meth-list">
          <div class="meth-item"><div class="meth-num">01</div><div class="meth-body"><div class="meth-title">Form a falsifiable hypothesis</div><div class="meth-desc">Every analysis starts with a specific claim that can be proven wrong. No vague directional bias allowed.</div></div></div>
          <div class="meth-item"><div class="meth-num">02</div><div class="meth-body"><div class="meth-title">Pull primary data</div><div class="meth-desc">On-chain data from node queries, exchange APIs, and aggregators  -  not repackaged sentiment from Twitter threads.</div></div></div>
          <div class="meth-item"><div class="meth-num">03</div><div class="meth-body"><div class="meth-title">Test across market regimes</div><div class="meth-desc">Bull, bear, and sideways. What works in one regime often fails in another. Both sides get published.</div></div></div>
          <div class="meth-item"><div class="meth-num">04</div><div class="meth-body"><div class="meth-title">Publish the uncertainty</div><div class="meth-desc">Confidence levels are stated explicitly. If the data is inconclusive, that is the finding  -  not a fabricated conclusion.</div></div></div>
          <div class="meth-item"><div class="meth-num">05</div><div class="meth-body"><div class="meth-title">Update when wrong</div><div class="meth-desc">When a call or thesis proves incorrect, a correction is published. No deleting posts. No pretending it didn't happen.</div></div></div>
        </div>
      </div>

      <!-- What This Site Covers -->
      <div style="margin-top:48px">
        <div class="sec-kicker">What {s['name']} Covers</div>
        <p class="abt-p">{s['hero_sub']}</p>
        <p class="abt-p">{s['footer_desc']}</p>
      </div>

      <!-- Contributors -->
      <div style="margin-top:48px">
        <div class="sec-kicker">Contributors</div>
        <div class="contrib-grid">
          {_contributors_html(s,'#020d06','#0d2b18','#c0ddc8','#2a5a38','var(--pri)')}
        </div>
      </div>

      <!-- Reader Comments -->
      <div style="margin-top:48px">
        <div class="sec-kicker">Reader Feedback</div>
        {_comments_html(s,'#020d06','#0d2b18','#5a8a6a','#2a5a38','var(--pri)')}
      </div>

    </div><!-- /LEFT -->

    <!-- RIGHT SIDEBAR -->
    <aside>

      <!-- Newsletter -->
      <div class="side-nl" id="subscribe">
        <h3>{s['nl_head']}</h3>
        <p>{s['nl_sub']}</p>
        <form id="abt-nl" onsubmit="nlSub('abt-nl',event)">
          <input type="email" class="nl-inp" placeholder="your@email.com" required>
          <button type="submit" class="nl-btn">Subscribe Free</button>
        </form>
      </div>

      <!-- Site Pillars -->
      <div class="sec-kicker" style="margin-top:8px">What You Get</div>
      <div class="pillar-list">
        <div class="pillar"><div class="pillar-dot"></div><div class="pillar-text"><strong>Live Market Data</strong>Real-time crypto prices from CoinGecko, updated every 90 seconds</div></div>
        <div class="pillar"><div class="pillar-dot"></div><div class="pillar-text"><strong>On-Chain Reports</strong>Exchange inflows, whale accumulation, mempool signals decoded</div></div>
        <div class="pillar"><div class="pillar-dot"></div><div class="pillar-text"><strong>Algo Breakdowns</strong>The full lifecycle of systematic strategies  -  build, test, deploy, retire</div></div>
        <div class="pillar"><div class="pillar-dot"></div><div class="pillar-text"><strong>No Hype, No Ads</strong>Independent research with no affiliate deals or price targets</div></div>
      </div>

      <!-- Recent Posts -->
      <div class="sec-kicker" style="margin-top:32px">Recent Analysis</div>
      <div id="recent-posts">
        <div class="recent-post" style="opacity:.35;pointer-events:none"><img class="recent-img" src="https://picsum.photos/seed/{seed+1}/160/112" alt="" loading="lazy"><div><div class="recent-title">First analysis publishing soon</div><div class="recent-meta">Coming soon</div></div></div>
        <div class="recent-post" style="opacity:.2;pointer-events:none"><img class="recent-img" src="https://picsum.photos/seed/{seed+2}/160/112" alt="" loading="lazy"><div><div class="recent-title">Research in preparation</div><div class="recent-meta">Coming soon</div></div></div>
        <div class="recent-post" style="opacity:.1;pointer-events:none"><img class="recent-img" src="https://picsum.photos/seed/{seed+3}/160/112" alt="" loading="lazy"><div><div class="recent-title">Signal study underway</div><div class="recent-meta">Coming soon</div></div></div>
      </div>

    </aside><!-- /SIDEBAR -->

  </div><!-- /two-col -->
</div><!-- /wrap -->

<!-- FOOTER -->
<footer class="foot">
  <div class="foot-in">
    <span class="foot-copy">© {s['name']} · {s['footer_desc']}</span>
    <div class="foot-links">
      <a href="./">Home</a>
      <a href="about.html">About</a>
      <a href="privacy.html">Privacy</a>
      <a href="terms.html">Terms</a>
      <a href="sms.html">SMS</a>
      <a href="meta-policy.html">Meta Policy</a>
    </div>
  </div>
</footer>

<script>
var abtDate=document.getElementById('abt-nav-date');
if(abtDate)abtDate.textContent=new Date().toLocaleDateString('en-US',{{weekday:'short',month:'short',day:'numeric'}});
/* live price ticker on about page */
(async function(){{
  try{{
    var d=await (await fetch('https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd&include_24hr_change=true',{{cache:'no-store'}})).json();
    var bb=document.getElementById('abt-btc'),eb=document.getElementById('abt-eth');
    function fmt(v){{return v>=1000?'$'+v.toFixed(0).replace(/\\B(?=(\\d{{3}})+(?!\\d))/g,','):'$'+v.toFixed(2);}}
    if(bb&&d.bitcoin)bb.textContent=fmt(d.bitcoin.usd);
    if(eb&&d.ethereum)eb.textContent=fmt(d.ethereum.usd);
  }}catch(e){{}}
}})();
function nlSub(id,e){{
  e.preventDefault();
  var f=document.getElementById(id);
  if(f)f.innerHTML='<p style="color:var(--pri);font-family:var(--fm);font-size:13px;font-weight:700;padding:10px 0">✓ Subscribed. Welcome to the list.</p>';
}}
(async function(){{
  try{{
    var r=await fetch('./articles.json');if(!r.ok)throw 0;
    var posts=await r.json();if(!posts||!posts.length)throw 0;
    var rp=document.getElementById('recent-posts');
    if(rp)rp.innerHTML=posts.slice(0,4).map(function(p){{
      var img=p.image||'https://picsum.photos/seed/'+(Math.abs(p.slug.charCodeAt(0)*31)%997+3)+'/160/112';
      return '<a href="./'+p.slug+'/" style="display:block"><div class="recent-post"><img class="recent-img" src="'+img+'" alt="'+p.title+'" loading="lazy"><div><div class="recent-title">'+p.title+'</div><div class="recent-meta">'+(p.date_iso||'')+'</div></div></div></a>';
    }}).join('');
  }}catch(e){{}}
}})();
{pxjs}
</script>
</body></html>"""


# ── TEMPLATE: STACK ────────────────────────────────────────────────────────────
def stack_index(s):
    cv = css_vars(s)
    ico_rocket = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4.5 16.5c-1.5 1.5-2 5-.5 5s3.5-1 5-2.5m-1-3-1.5-1.5M17 2S22 7 22 7s-7.5 4.5-10.5 7.5c-1.5 1.5-3 2.5-4.5 2.5s-3-1-3-3 1-3 2.5-4.5C9.5 6.5 14 2 14 2z"/><circle cx="13" cy="11" r="1"/></svg>'
    ico_bar = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>'
    ico_check = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>'
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{s['name']} - {s['tagline']}</title>
<meta name="description" content="{s['hero_sub']}">
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
:root{{{cv}}}
body{{font-family:var(--fb);background:var(--bg);color:var(--txt);font-size:15px;line-height:1.7;min-height:100vh}}
a{{color:var(--pri);text-decoration:none}}
.stk-bar{{display:flex;align-items:center;justify-content:space-between;padding:16px 48px;position:fixed;top:0;width:100%;z-index:99;transition:background .35s,border-color .35s}}
.stk-bar.solid{{background:var(--bg)ee;border-bottom:1px solid var(--brd);backdrop-filter:blur(14px)}}
.stk-brand{{font-size:20px;font-weight:900;letter-spacing:-0.5px;color:#fff;transition:color .3s;text-decoration:none}}
.stk-bar.solid .stk-brand{{color:var(--txt)}}
.stk-brand-acc{{color:var(--pri)}}
.stk-bar-nav{{display:flex;gap:28px}}
.stk-bar-nav a{{font-size:13px;color:rgba(255,255,255,.75);font-weight:500;transition:color .2s}}
.stk-bar.solid .stk-bar-nav a{{color:var(--mut)}}
.stk-bar-nav a:hover{{color:#fff}}
.stk-bar.solid .stk-bar-nav a:hover{{color:var(--txt)}}
.stk-hero{{position:relative;height:88vh;min-height:540px;max-height:820px;display:flex;align-items:center;justify-content:center;overflow:hidden}}
.stk-hero-bg{{position:absolute;inset:0;background:var(--bg2)}}
.stk-hero-bg img{{width:100%;height:100%;object-fit:cover;display:block;opacity:0;transition:opacity 1.2s}}
.stk-hero-ov{{position:absolute;inset:0;background:linear-gradient(to bottom,rgba(0,0,0,.55) 0%,rgba(0,0,0,.35) 50%,rgba(0,0,0,.75) 100%)}}
.stk-hero-content{{position:relative;z-index:2;text-align:center;padding:0 24px;max-width:820px}}
.stk-hero-badge{{display:inline-block;background:var(--pri);color:#000;font-size:10px;font-weight:800;letter-spacing:2px;text-transform:uppercase;padding:5px 14px;border-radius:2px;margin-bottom:22px}}
.stk-hero h1{{font-size:clamp(32px,5vw,62px);font-weight:900;line-height:1.08;letter-spacing:-2px;color:#fff;margin-bottom:18px}}
.stk-hero p{{font-size:17px;color:rgba(255,255,255,.75);max-width:540px;margin:0 auto 34px;line-height:1.75}}
.stk-hero-btns{{display:flex;gap:14px;justify-content:center;flex-wrap:wrap}}
.stk-cta{{background:var(--pri);color:#000;border-radius:4px;padding:14px 32px;font-size:15px;font-weight:800;transition:transform .2s,opacity .2s}}
.stk-cta:hover{{transform:translateY(-2px);opacity:.9}}
.stk-cta2{{border:1.5px solid rgba(255,255,255,.5);color:#fff;border-radius:4px;padding:13px 28px;font-size:15px;font-weight:600;transition:all .2s}}
.stk-cta2:hover{{border-color:#fff;background:rgba(255,255,255,.1)}}
.stk-scroll-hint{{position:absolute;bottom:28px;left:50%;transform:translateX(-50%);z-index:2;color:rgba(255,255,255,.45);font-size:11px;letter-spacing:1px;text-transform:uppercase;display:flex;flex-direction:column;align-items:center;gap:7px}}
.stk-scroll-arr{{animation:sbarr 1.8s ease-in-out infinite}}
@keyframes sbarr{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(7px)}}}}
.stk-stats{{display:grid;grid-template-columns:repeat(4,1fr);background:var(--bg2);border-bottom:1px solid var(--brd)}}
.stk-stat{{padding:22px 16px;text-align:center;border-right:1px solid var(--brd)}}
.stk-stat:last-child{{border-right:none}}
.stk-stat-num{{font-size:24px;font-weight:900;color:var(--pri);letter-spacing:-1px}}
.stk-stat-label{{font-size:11px;color:var(--mut);margin-top:3px;text-transform:uppercase;letter-spacing:.5px}}
.stk-vp{{padding:52px 48px;background:var(--bg2);border-bottom:1px solid var(--brd)}}
.stk-vp-in{{max-width:1200px;margin:0 auto;display:grid;grid-template-columns:repeat(3,1fr);gap:24px}}
.stk-vp-card{{padding:28px;border:1px solid var(--brd);border-radius:10px;background:var(--bg);transition:border-color .25s}}
.stk-vp-card:hover{{border-color:var(--pri2)}}
.stk-vp-icon{{width:44px;height:44px;border-radius:10px;background:linear-gradient(135deg,var(--pri)22,var(--pri2)11);display:flex;align-items:center;justify-content:center;color:var(--pri);margin-bottom:14px}}
.stk-vp-title{{font-size:17px;font-weight:700;margin-bottom:8px}}
.stk-vp-desc{{font-size:14px;color:var(--mut);line-height:1.7}}
/* featured strip */
.stk-feat-wrap{{max-width:1200px;margin:0 auto;padding:40px 48px 28px}}
.stk-feat-hd{{font-size:10px;font-weight:800;text-transform:uppercase;letter-spacing:2px;color:var(--mut);margin-bottom:20px;display:flex;align-items:center;gap:12px}}.stk-feat-hd::after{{content:'';flex:1;height:1px;background:var(--brd)}}
.stk-feat-grid{{display:grid;grid-template-columns:1.65fr 1fr;gap:20px}}
.stk-feat-main{{border:1px solid var(--brd);border-radius:12px;overflow:hidden;background:var(--bg2);transition:border-color .2s,transform .15s;text-decoration:none;display:block;color:inherit}}.stk-feat-main:hover{{border-color:var(--pri2);transform:translateY(-3px)}}
.stk-feat-img{{width:100%;height:280px;object-fit:cover;display:block;background:var(--sur)}}
.stk-feat-body{{padding:20px 22px}}
.stk-feat-lbl{{font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:2px;color:var(--pri);margin-bottom:8px}}
.stk-feat-title{{font-size:clamp(16px,2.2vw,22px);font-weight:800;line-height:1.28;color:var(--txt);margin-bottom:8px}}
.stk-feat-desc{{font-size:13px;color:var(--mut);line-height:1.7}}
.stk-feat-meta{{font-size:11px;color:var(--mut);margin-top:10px;display:flex;gap:8px;align-items:center}}
.stk-feat-cta{{display:inline-block;color:var(--pri);font-weight:700;font-size:12px;margin-top:10px}}
.stk-feat-side{{display:flex;flex-direction:column;gap:12px}}
.stk-feat-mini{{display:flex;gap:0;border:1px solid var(--brd);border-radius:10px;overflow:hidden;background:var(--bg2);transition:border-color .2s,transform .15s;text-decoration:none;color:inherit;align-items:stretch}}.stk-feat-mini:hover{{border-color:var(--pri2);transform:translateY(-2px)}}
.stk-feat-mini-img{{width:86px;height:86px;object-fit:cover;flex-shrink:0;background:var(--sur)}}
.stk-feat-mini-body{{padding:10px 14px;flex:1}}
.stk-feat-mini-lbl{{font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:2px;color:var(--pri);margin-bottom:4px}}
.stk-feat-mini-title{{font-size:13px;font-weight:600;line-height:1.4;color:var(--txt)}}
.stk-feat-mini-date{{font-size:10px;color:var(--mut);margin-top:4px}}
/* topics */
.stk-topics{{padding:12px 48px;background:var(--bg2);border-top:1px solid var(--brd);border-bottom:1px solid var(--brd);display:flex;align-items:center;gap:8px;overflow-x:auto;scrollbar-width:none}}
.stk-topics::-webkit-scrollbar{{display:none}}
.stk-topics-lbl{{font-size:9px;font-weight:800;text-transform:uppercase;letter-spacing:2px;color:var(--mut);flex-shrink:0;margin-right:4px}}
.stk-topic{{flex-shrink:0;font-size:11px;font-weight:600;padding:5px 12px;border:1px solid var(--brd);border-radius:100px;color:var(--mut);cursor:pointer;transition:all .2s;white-space:nowrap}}.stk-topic:hover{{border-color:var(--pri);color:var(--pri);background:var(--bg)}}
.stk-shelf{{padding:52px 48px;max-width:1200px;margin:0 auto}}
.stk-shelf-hd{{display:flex;align-items:center;gap:14px;margin-bottom:28px}}
.stk-shelf-hd h2{{font-size:11px;font-weight:800;text-transform:uppercase;letter-spacing:2px;color:var(--txt)}}
.stk-shelf-hd::after{{content:'';flex:1;height:1px;background:var(--brd)}}
.stk-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:20px}}
.stk-item{{background:var(--bg2);border:1px solid var(--brd);border-radius:10px;overflow:hidden;transition:border-color .2s,transform .15s}}
.stk-item:hover{{border-color:var(--pri2);transform:translateY(-3px)}}
.stk-item img{{width:100%;height:170px;object-fit:cover;display:block}}
.stk-item-body{{padding:18px 20px}}
.stk-item-cat{{font-size:10px;font-weight:700;color:var(--pri);text-transform:uppercase;letter-spacing:2px;margin-bottom:6px}}
.stk-item h3{{font-size:16px;font-weight:700;line-height:1.4;color:var(--txt);margin-bottom:8px}}
.stk-item p{{font-size:13px;color:var(--mut);line-height:1.7}}
.stk-item-meta{{font-size:11px;color:var(--mut);display:flex;justify-content:space-between;margin-top:10px;padding-top:10px;border-top:1px solid var(--brd)}}
.stk-item-read{{color:var(--pri);font-weight:600}}
.stk-letter{{background:var(--sur);border-top:1px solid var(--brd);border-bottom:1px solid var(--brd);padding:72px 48px;text-align:center}}
.stk-letter h2{{font-size:clamp(22px,3vw,34px);font-weight:800;margin-bottom:12px}}
.stk-letter p{{color:var(--mut);font-size:15px;margin-bottom:28px;max-width:500px;margin-left:auto;margin-right:auto}}
.stk-letter-form{{display:flex;gap:10px;max-width:440px;margin:0 auto}}
.stk-letter-input{{flex:1;background:var(--bg);border:1px solid var(--brd);border-radius:6px;padding:12px 16px;color:var(--txt);font-size:14px;outline:none;transition:border-color .2s}}
.stk-letter-input:focus{{border-color:var(--pri)}}
.stk-letter-btn{{background:var(--pri);color:#000;border:none;border-radius:6px;padding:12px 24px;font-size:14px;font-weight:700;cursor:pointer;white-space:nowrap;transition:opacity .2s}}
.stk-letter-btn:hover{{opacity:.85}}
.stk-base{{padding:28px 48px;border-top:1px solid var(--brd);display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px}}
.stk-base-copy{{font-size:12px;color:var(--mut)}}
.stk-base-links{{display:flex;gap:20px}}.stk-base-links a{{font-size:12px;color:var(--mut);transition:color .2s}}.stk-base-links a:hover{{color:var(--txt)}}
.reveal{{opacity:0;transform:translateY(20px);transition:opacity .6s,transform .6s}}
.reveal.visible{{opacity:1;transform:none}}
@media(max-width:900px){{.stk-stats{{grid-template-columns:1fr 1fr}}.stk-stat:nth-child(2){{border-right:none}}.stk-feat-grid{{grid-template-columns:1fr}}}}
@media(max-width:700px){{.stk-bar{{padding:12px 16px}}.stk-shelf{{padding:40px 16px}}.stk-feat-wrap{{padding:28px 16px 16px}}.stk-topics{{padding:12px 16px}}.stk-vp{{padding:40px 16px}}.stk-vp-in{{grid-template-columns:1fr}}.stk-letter{{padding:48px 16px}}.stk-letter-form{{flex-direction:column}}.stk-base{{padding:20px 16px;flex-direction:column;text-align:center}}.stk-hero h1{{letter-spacing:-1px}}}}
</style>
</head>
<body>

<nav class="stk-bar" id="stk-bar">
  <a href="./" class="stk-brand">{s['name'].split()[0]}<span class="stk-brand-acc">{s['name'][len(s['name'].split()[0]):]}</span></a>
  <div class="stk-bar-nav">
    <a href="./">Home</a><a href="about.html">About</a><a href="privacy.html">Privacy</a>
  </div>
</nav>

<div class="stk-hero">
  <div class="stk-hero-bg"><img id="pxl-img" alt="{s['name']}"></div>
  <div class="stk-hero-ov"></div>
  <div class="stk-hero-content">
    <div class="stk-hero-badge">{s['category']}</div>
    <h1>{s['tagline']}</h1>
    <p>{s['hero_sub']}</p>
    <div class="stk-hero-btns">
      <a href="#latest" class="stk-cta">Read Articles →</a>
      <a href="about.html" class="stk-cta2">About the Author</a>
    </div>
  </div>
  <div class="stk-scroll-hint">
    <span>Scroll</span>
    <div class="stk-scroll-arr"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"/></svg></div>
  </div>
</div>

<div class="stk-stats">
  <div class="stk-stat"><div class="stk-stat-num">100+</div><div class="stk-stat-label">Guides</div></div>
  <div class="stk-stat"><div class="stk-stat-num">5K+</div><div class="stk-stat-label">Readers</div></div>
  <div class="stk-stat"><div class="stk-stat-num">Free</div><div class="stk-stat-label">Always</div></div>
  <div class="stk-stat"><div class="stk-stat-num">Expert</div><div class="stk-stat-label">Vetted</div></div>
</div>

<!-- FEATURED ARTICLES UPFRONT -->
<div class="stk-feat-wrap reveal">
  <div class="stk-feat-hd">Featured</div>
  <div class="stk-feat-grid" id="stk-feat"></div>
</div>

<!-- TOPICS STRIP -->
<div class="stk-topics">
  <span class="stk-topics-lbl">Topics</span>
  {"".join(f'<span class="stk-topic">{t}</span>' for t in s.get("stack_topics",["Online Business","Side Hustles","E-Commerce","Digital Marketing","Freelancing","Automation","SEO","Revenue Growth"]))}
</div>

<div class="stk-vp reveal">
  <div class="stk-vp-in">
    <div class="stk-vp-card">
      <div class="stk-vp-icon">{ico_rocket}</div>
      <div class="stk-vp-title">Launch Faster</div>
      <div class="stk-vp-desc">Step-by-step playbooks built for real business owners who don't have time to waste on fluff.</div>
    </div>
    <div class="stk-vp-card">
      <div class="stk-vp-icon">{ico_bar}</div>
      <div class="stk-vp-title">Revenue First</div>
      <div class="stk-vp-desc">Every guide is focused on moving your bottom line with tactics that actually convert.</div>
    </div>
    <div class="stk-vp-card">
      <div class="stk-vp-icon">{ico_check}</div>
      <div class="stk-vp-title">Battle-Tested</div>
      <div class="stk-vp-desc">Strategies drawn from real {s['category'].lower()} experience  -  not theory, not templates.</div>
    </div>
  </div>
</div>

<div class="stk-shelf" id="latest">
  <div class="stk-shelf-hd reveal"><h2>Latest Articles</h2></div>
  <div class="stk-grid reveal" id="stk-grid"></div>
</div>

<div class="stk-shelf">
  <div class="stk-shelf-hd reveal" id="more-hd" style="display:none"><h2>More from {s['name']}</h2></div>
  <div class="stk-grid reveal" id="more-grid"></div>
</div>

<div class="stk-letter reveal">
  <h2>{s['nl_head']}</h2>
  <p>{s['nl_sub']}</p>
  <form id="stk-nl" onsubmit="nlSub(event)">
    <div class="stk-letter-form">
      <input type="email" class="stk-letter-input" placeholder="your@email.com" required>
      <button type="submit" class="stk-letter-btn">Subscribe Free</button>
    </div>
  </form>
</div>

<div class="stk-base">
  <span class="stk-base-copy">© {s['name']} - by {s['author']}</span>
  <div class="stk-base-links"><a href="./">Home</a><a href="about.html">About</a><a href="privacy.html">Privacy</a><a href="terms.html">Terms</a><a href="sms.html">SMS</a><a href="meta-policy.html">Meta Policy</a></div>
</div>

<script>
var bar=document.getElementById('stk-bar');
window.addEventListener('scroll',function(){{if(window.scrollY>60)bar.classList.add('solid');else bar.classList.remove('solid');}},{{passive:true}});

async function loadPosts(){{
  var sg=document.getElementById('stk-grid');
  var mg=document.getElementById('more-grid');
  var mh=document.getElementById('more-hd');
  try{{
    var r=await fetch('./articles.json');if(!r.ok)throw 0;
    var posts=await r.json();if(!posts.length)throw 0;
    // Featured strip
    var feat=document.getElementById('stk-feat');
    if(feat&&posts.length>=1){{
      var fp=posts[0];
      var sp=posts.slice(1,4);
      feat.innerHTML='<a href="./'+fp.slug+'/" class="stk-feat-main">'+(fp.image?'<img class="stk-feat-img" src="'+fp.image+'" alt="'+fp.title+'" loading="lazy">':'<div class="stk-feat-img"></div>')+'<div class="stk-feat-body"><div class="stk-feat-lbl">{s['category']}</div><div class="stk-feat-title">'+fp.title+'</div><div class="stk-feat-desc">'+(fp.meta_description||'').slice(0,140)+'</div><div class="stk-feat-meta">'+(fp.date_iso||'')+'</div><span class="stk-feat-cta">Read full article →</span></div></a><div class="stk-feat-side">'+sp.map(function(p){{return '<a href="./'+p.slug+'/" class="stk-feat-mini">'+(p.image?'<img class="stk-feat-mini-img" src="'+p.image+'" alt="'+p.title+'" loading="lazy">':'<div class="stk-feat-mini-img"></div>')+'<div class="stk-feat-mini-body"><div class="stk-feat-mini-lbl">{s['category']}</div><div class="stk-feat-mini-title">'+p.title+'</div><div class="stk-feat-mini-date">'+(p.date_iso||'')+'</div></div></a>';}}).join('')+'</div>';
    }}
    function card(p){{return '<a href="./'+p.slug+'/" style="display:block"><div class="stk-item">'+(p.image?'<img src="'+p.image+'" alt="'+p.title+'" loading="lazy">':'')+'<div class="stk-item-body"><div class="stk-item-cat">{s['category']}</div><h3>'+p.title+'</h3><p>'+(p.meta_description||'').slice(0,110)+'</p><div class="stk-item-meta"><span>'+(p.date_iso||'')+'</span><span class="stk-item-read">Read →</span></div></div></div></a>';}}
    if(sg)sg.innerHTML=posts.slice(4,10).map(card).join('');
    if(mg&&posts.length>10){{mg.innerHTML=posts.slice(10,16).map(card).join('');if(mh)mh.style.display='';}}
  }}catch(e){{
    if(sg)sg.innerHTML='<div class="stk-item"><div class="stk-item-body"><div class="stk-item-cat">Coming Soon</div><h3>Articles publishing shortly</h3><p>The content system is warming up. Check back soon.</p></div></div>';
  }}
}}
function nlSub(e){{e.preventDefault();document.getElementById('stk-nl').innerHTML='<div style="color:var(--pri);font-size:15px;font-weight:600;padding:8px">✓ You\'re in. Check your inbox.</div>';}}
const obs=new IntersectionObserver(entries=>entries.forEach(en=>{{if(en.isIntersecting){{en.target.classList.add('visible');obs.unobserve(en.target);}}}}),{{threshold:.1}});
document.querySelectorAll('.reveal').forEach(el=>obs.observe(el));
loadPosts();
{_pexels_js(s)}
</script>
</body></html>"""


def stack_about(s):
    cv = css_vars(s)
    ini = ''.join(w[0] for w in s['author'].split() if w)
    story = _story_html(s, 'abt-p')
    banner = _pexels_banner('220px')
    pxjs   = _pexels_js(s)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>About {s['author']} - {s['name']}</title>
<meta name="description" content="{s['footer_desc']}">
<style>
/* === reset === */
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
:root{{{cv}}}
body{{font-family:var(--fb);background:var(--bg);color:var(--txt);font-size:15px;line-height:1.7;min-height:100vh}}
a{{color:var(--pri);text-decoration:none}}a:hover{{opacity:.8}}
/* === nav === */
.stk-bar{{display:flex;align-items:center;justify-content:space-between;padding:16px 48px;border-bottom:1px solid var(--brd);background:var(--bg);position:sticky;top:0;z-index:99}}
.stk-brand{{font-size:18px;font-weight:800;color:var(--txt);letter-spacing:-0.5px;text-decoration:none}}
.stk-brand span{{color:var(--pri)}}.stk-bar-nav{{display:flex;gap:28px}}.stk-bar-nav a{{font-size:13px;color:var(--mut)}}.stk-bar-nav a:hover{{color:var(--txt)}}
/* === author hero band === */
.abt-hero{{background:linear-gradient(135deg,var(--bg2) 0%,var(--bg) 80%);border-bottom:1px solid var(--brd);padding:56px 48px;display:flex;align-items:center;gap:36px}}
.abt-avi{{width:84px;height:84px;border-radius:50%;background:var(--pri);display:flex;align-items:center;justify-content:center;font-size:28px;font-weight:800;color:#000;flex-shrink:0;border:3px solid var(--brd)}}
.abt-hero-name{{font-size:clamp(22px,3vw,36px);font-weight:800;margin-bottom:6px;letter-spacing:-0.5px}}
.abt-hero-title{{font-size:14px;color:var(--pri);font-weight:600}}
.abt-hero-cat{{font-size:11px;color:var(--mut);margin-top:4px}}
/* === body === */
.abt-content{{max-width:740px;margin:0 auto;padding:52px 48px}}
.abt-section{{margin-bottom:40px}}
.abt-section h2{{font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:2px;color:var(--pri);border-bottom:1px solid var(--brd);padding-bottom:10px;margin-bottom:20px}}
.abt-p{{color:var(--mut);line-height:1.9;margin-bottom:14px}}
/* === highlight box === */
.abt-highlight{{background:var(--bg2);border:1px solid var(--brd);border-radius:8px;padding:20px 22px;margin-bottom:40px}}
.abt-highlight-label{{font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:2px;color:var(--pri);margin-bottom:8px}}
.abt-highlight p{{font-size:14px;color:var(--txt);line-height:1.75}}
/* === newsletter === */
.abt-nl{{background:var(--bg2);border:1px solid var(--brd);border-radius:8px;padding:28px;margin-top:8px}}
.abt-nl h3{{font-size:18px;font-weight:700;margin-bottom:8px}}.abt-nl p{{color:var(--mut);margin-bottom:18px}}
.stk-letter-form{{display:flex;gap:10px;max-width:420px}}
.stk-letter-input{{flex:1;background:var(--bg);border:1px solid var(--brd);border-radius:6px;padding:10px 14px;color:var(--txt);font-size:14px;outline:none;transition:border-color .2s}}
.stk-letter-input:focus{{border-color:var(--pri)}}.stk-letter-input::placeholder{{color:var(--mut)}}
.stk-letter-btn{{background:var(--pri);color:#000;border:none;border-radius:6px;padding:10px 20px;font-size:14px;font-weight:700;cursor:pointer;transition:background .2s}}
.stk-letter-btn:hover{{background:var(--pri2)}}.stk-letter-ok{{color:var(--pri);font-weight:600;padding:6px 0}}
/* === footer === */
.stk-base{{padding:24px 48px;border-top:1px solid var(--brd);display:flex;justify-content:space-between;flex-wrap:wrap;gap:10px;margin-top:20px}}
.stk-base-copy,.stk-base-links a{{font-size:12px;color:var(--mut)}}.stk-base-links{{display:flex;gap:20px}}
@media(max-width:700px){{.stk-bar{{padding:12px 16px}}.abt-hero{{padding:36px 16px;flex-direction:column;gap:20px}}.abt-content{{padding:36px 16px}}.stk-letter-form{{flex-direction:column}}.stk-base{{padding:20px 16px}}}}
</style>
</head>
<body>

<!-- nav -->
<div class="stk-bar">
  <a href="./" class="stk-brand">{s['name'].split()[0]}<span>{s['name'][len(s['name'].split()[0]):]}</span></a>
  <nav class="stk-bar-nav"><a href="./">Home</a><a href="about.html">About</a></nav>
</div>

<!-- author-hero -->
<div class="abt-hero">
  <div class="abt-avi">{ini}</div>
  <div>
    <div class="abt-hero-name">{s['author']}</div>
    <div class="abt-hero-title">{s['author_title']}</div>
    <div class="abt-hero-cat">{s['category']}</div>
  </div>
</div>

<!-- pexels-banner -->
{banner}

<!-- main-content -->
<div class="abt-content">

  <!-- section: background story -->
  <div class="abt-section">
    <h2>Background</h2>
    {story}
  </div>

  <!-- section: what this site is about -->
  <div class="abt-highlight">
    <div class="abt-highlight-label">What This Site Covers</div>
    <p>{s['hero_sub']}</p>
  </div>

  <!-- section: site mission -->
  <div class="abt-section">
    <h2>About {s['name']}</h2>
    <p class="abt-p">{s['footer_desc']}</p>
    <p class="abt-p">Content in the {s['category']} space is published here on an ongoing basis. No sponsored content, no paid placements - just the analysis and frameworks I find genuinely useful.</p>
  </div>

  <!-- section: newsletter -->
  <div class="abt-nl">
    <h3>{s['nl_head']}</h3>
    <p>{s['nl_sub']}</p>
    <form id="abt-nl" onsubmit="nlSub(event)">
      <div class="stk-letter-form">
        <input type="email" class="stk-letter-input" placeholder="your@email.com" required>
        <button type="submit" class="stk-letter-btn">Subscribe</button>
      </div>
    </form>
  </div>

</div>

<!-- section: contributors -->
<div style="max-width:860px;margin:0 auto;padding:0 48px 32px">
  <div class="abt-section-hd" style="font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:1.5px;color:var(--mut);margin-bottom:14px">Contributors</div>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px">
    {_contributors_html(s,'var(--sur)','var(--brd)','var(--txt)','var(--mut)','var(--pri)')}
  </div>
</div>

<!-- section: comments -->
<div style="max-width:860px;margin:0 auto;padding:0 48px 40px">
  <div class="abt-section-hd" style="font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:1.5px;color:var(--mut);margin-bottom:14px">Reader Comments</div>
  <div style="background:var(--sur);border:1px solid var(--brd);border-radius:10px;padding:4px 20px">
    {_comments_html(s,'var(--sur)','var(--brd)','var(--txt)','var(--mut)','var(--pri)')}
  </div>
</div>

<!-- footer -->
<div class="stk-base">
  <span class="stk-base-copy">© {s['name']}</span>
  <div class="stk-base-links"><a href="./">Home</a><a href="about.html">About</a><a href="privacy.html">Privacy Policy</a><a href="terms.html">Terms</a><a href="sms.html">SMS Policy</a><a href="meta-policy.html">Meta Policy</a></div>
</div>

<script>
function nlSub(e){{e.preventDefault();e.target.innerHTML='<div class="stk-letter-ok">✓ Subscribed.</div>';}}
{pxjs}
</script>
</body></html>"""


# ── TEMPLATE: GRID (light, minimal) ───────────────────────────────────────────
def grid_index(s):
    _tmpl = BASE / "templates" / f"{s['id']}-index.html"
    if _tmpl.exists():
        return _tmpl.read_text(encoding="utf-8")
    cv = css_vars(s)
    ico_cart  = '<svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="9" cy="21" r="1"/><circle cx="20" cy="21" r="1"/><path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"/></svg>'
    ico_trend = '<svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>'
    ico_users = '<svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>'
    ico_bar   = '<svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>'
    ico_quote = '<svg width="32" height="32" viewBox="0 0 24 24" fill="currentColor" stroke="none"><path d="M11.192 15.757c0-.88-.23-1.618-.69-2.217-.326-.412-.768-.683-1.327-.812-.55-.128-1.07-.137-1.54-.028-.16-.95.1-1.95.78-3 .53-.81 1.24-1.48 2.13-2.02L8.89 6c-1.49.9-2.66 2.1-3.5 3.6-.85 1.5-1.27 3.04-1.27 4.6 0 1.44.35 2.58 1.06 3.42.7.84 1.63 1.26 2.78 1.26.97 0 1.77-.3 2.4-.9.63-.6.94-1.38.94-2.34zm7.44 0c0-.88-.23-1.618-.69-2.217-.326-.42-.77-.692-1.327-.817-.56-.124-1.074-.13-1.54-.022-.16-.95.1-1.95.78-3 .53-.81 1.24-1.48 2.13-2.02l-1.65-1.67c-1.49.9-2.66 2.1-3.5 3.6-.85 1.5-1.27 3.04-1.27 4.6 0 1.44.35 2.58 1.06 3.42.7.84 1.63 1.26 2.78 1.26.97 0 1.77-.3 2.4-.9.63-.6.94-1.38.94-2.34z"/></svg>'
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{s['name']} - {s['tagline']}</title>
<meta name="description" content="{s['hero_sub']}">
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
:root{{{cv}}}
body{{font-family:var(--fb);background:var(--bg);color:var(--txt);font-size:15px;line-height:1.7}}
a{{color:inherit;text-decoration:none}}
@keyframes fadeUp{{from{{opacity:0;transform:translateY(18px)}}to{{opacity:1;transform:translateY(0)}}}}
@keyframes slideIn{{from{{opacity:0;transform:translateX(-12px)}}to{{opacity:1;transform:translateX(0)}}}}
@keyframes shimmer{{0%{{background-position:200% 0}}100%{{background-position:-200% 0}}}}
.reveal{{opacity:0;transform:translateY(18px);transition:opacity .5s ease,transform .5s ease}}.reveal.visible{{opacity:1;transform:translateY(0)}}
/* nav */
.gn{{background:#fff;border-bottom:2px solid var(--pri);padding:0 48px;display:flex;align-items:center;justify-content:space-between;height:64px;position:sticky;top:0;z-index:99;box-shadow:0 2px 16px rgba(0,0,0,.07)}}
.gn-logo{{font-size:19px;font-weight:800;color:var(--pri);letter-spacing:-.5px}}
.gn-links{{display:flex;gap:24px}}.gn-links a{{font-size:13px;color:var(--mut);font-weight:500;transition:color .2s;padding:4px 0;border-bottom:2px solid transparent}}.gn-links a:hover{{color:var(--pri);border-bottom-color:var(--pri)}}
.gn-cta{{background:var(--pri);color:#fff;border:none;border-radius:6px;padding:9px 20px;font-size:13px;font-weight:700;cursor:pointer;transition:all .2s;box-shadow:0 2px 8px rgba(249,115,22,.3)}}.gn-cta:hover{{background:var(--pri2);transform:translateY(-1px);box-shadow:0 4px 14px rgba(249,115,22,.4)}}
/* hero */
.gh{{background:linear-gradient(135deg,var(--bg2) 0%,#fff5f0 100%);border-bottom:1px solid var(--brd);padding:60px 48px 56px;animation:fadeUp .6s ease both}}
.gh-eyebrow{{font-size:11px;font-weight:700;color:var(--pri);text-transform:uppercase;letter-spacing:3px;margin-bottom:18px;display:flex;align-items:center;gap:8px}}
.gh-eyebrow::before{{content:'';width:24px;height:2px;background:var(--pri);flex-shrink:0}}
.gh-h1{{font-size:clamp(28px,3.8vw,50px);font-weight:800;line-height:1.1;color:var(--txt);max-width:560px;margin-bottom:16px}}
.gh-sub{{font-size:16px;color:var(--mut);max-width:480px;line-height:1.9;margin-bottom:36px}}
.gh-grid{{display:grid;grid-template-columns:1fr 340px;gap:24px;align-items:start}}
.gh-feat{{display:flex;flex-direction:column;border-radius:12px;overflow:hidden;border:1px solid var(--brd);transition:box-shadow .25s,transform .25s;text-decoration:none;background:#fff}}.gh-feat:hover{{box-shadow:0 12px 40px rgba(249,115,22,.15);transform:translateY(-3px)}}
.gh-feat-img{{width:100%;height:320px;object-fit:cover;display:block;background:linear-gradient(135deg,var(--sur),var(--brd))}}
.gh-feat-body{{padding:22px 24px 24px;flex:1}}
.gh-feat-tag{{font-size:10px;font-weight:700;color:var(--pri);text-transform:uppercase;letter-spacing:2px;margin-bottom:10px}}
.gh-feat-title{{font-size:20px;font-weight:800;line-height:1.3;color:var(--txt);margin-bottom:8px}}
.gh-feat-desc{{font-size:13px;color:var(--mut);line-height:1.7;margin-bottom:12px}}
.gh-feat-meta{{font-size:11px;color:var(--mut);display:flex;align-items:center;gap:6px}}
.gh-feat-meta::before{{content:'';width:20px;height:1px;background:var(--pri);flex-shrink:0}}
.gh-side{{display:flex;flex-direction:column;gap:12px}}
.gh-sub-art{{display:flex;border:1px solid var(--brd);border-radius:10px;overflow:hidden;background:#fff;transition:box-shadow .2s,transform .2s;text-decoration:none;color:inherit}}.gh-sub-art:hover{{box-shadow:0 6px 20px rgba(249,115,22,.12);transform:translateY(-2px)}}
.gh-sub-img{{width:88px;height:88px;object-fit:cover;flex-shrink:0;background:var(--sur)}}
.gh-sub-body{{padding:10px 14px;flex:1}}
.gh-sub-tag{{font-size:9px;font-weight:700;color:var(--pri);text-transform:uppercase;letter-spacing:2px;margin-bottom:4px}}
.gh-sub-title{{font-size:13px;font-weight:600;line-height:1.4;color:var(--txt)}}
.gh-sub-date{{font-size:10px;color:var(--mut);margin-top:5px}}
/* topics */
.gt{{padding:20px 48px;background:#fff;border-bottom:1px solid var(--brd);display:flex;align-items:center;gap:10px;flex-wrap:wrap}}
.gt-label{{font-size:11px;font-weight:700;color:var(--mut);text-transform:uppercase;letter-spacing:2px;flex-shrink:0;margin-right:4px}}
.gt-tag{{font-size:12px;font-weight:600;color:var(--mut);background:var(--bg2);border:1px solid var(--brd);border-radius:100px;padding:5px 14px;transition:all .2s;cursor:pointer}}.gt-tag:hover{{background:var(--pri);color:#fff;border-color:var(--pri);transform:translateY(-1px)}}
/* value props */
.gv{{padding:52px 48px;background:var(--bg2);border-bottom:1px solid var(--brd)}}
.gv-label{{font-size:11px;font-weight:700;color:var(--pri);text-transform:uppercase;letter-spacing:3px;margin-bottom:32px;text-align:center}}
.gv-grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:18px;max-width:1120px;margin:0 auto}}
.gv-card{{border:1px solid var(--brd);border-radius:12px;padding:24px 20px;text-align:center;background:#fff;transition:all .25s;cursor:default}}.gv-card:hover{{border-color:var(--pri);box-shadow:0 8px 28px rgba(249,115,22,.12);transform:translateY(-3px)}}
.gv-icon{{color:var(--pri);margin-bottom:14px;display:flex;align-items:center;justify-content:center}}
.gv-head{{font-size:14px;font-weight:800;color:var(--txt);margin-bottom:8px}}
.gv-body{{font-size:12px;color:var(--mut);line-height:1.7}}
/* daily quote */
.gq{{background:var(--pri);padding:52px 48px;position:relative;overflow:hidden}}
.gq::before{{content:'';position:absolute;top:-60px;right:-60px;width:200px;height:200px;background:rgba(255,255,255,.06);border-radius:50%}}
.gq::after{{content:'';position:absolute;bottom:-40px;left:20px;width:120px;height:120px;background:rgba(255,255,255,.04);border-radius:50%}}
.gq-inner{{max-width:760px;margin:0 auto;position:relative;text-align:center}}
.gq-label{{font-size:10px;font-weight:700;color:rgba(255,255,255,.7);text-transform:uppercase;letter-spacing:3px;margin-bottom:16px}}
.gq-icon{{color:rgba(255,255,255,.3);margin-bottom:16px;display:flex;justify-content:center}}
.gq-text{{font-size:clamp(17px,2.2vw,23px);font-weight:600;color:#fff;line-height:1.55;font-style:italic;margin-bottom:16px}}
.gq-attr{{font-size:12px;color:rgba(255,255,255,.7);font-style:normal}}
/* pexels banner */
/* articles */
.gaa{{padding:56px 48px;max-width:1240px;margin:0 auto}}
.gaa-hd{{display:flex;align-items:center;gap:12px;margin-bottom:28px;padding-bottom:12px;border-bottom:2px solid var(--brd)}}
.gaa-hd-text{{font-size:12px;font-weight:800;text-transform:uppercase;letter-spacing:2px;color:var(--mut)}}
.gaa-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:22px}}
.gac{{display:flex;flex-direction:column;background:#fff;border:1px solid var(--brd);border-radius:12px;overflow:hidden;transition:all .25s;text-decoration:none;color:inherit}}.gac:hover{{box-shadow:0 10px 32px rgba(0,0,0,.1);transform:translateY(-3px);border-color:var(--brd)}}
.gac-img{{width:100%;height:185px;object-fit:cover;display:block;background:var(--sur);transition:transform .4s}}.gac:hover .gac-img{{transform:scale(1.03)}}
.gac-img-wrap{{overflow:hidden;flex-shrink:0}}
.gac-body{{padding:18px 20px 12px;flex:1;display:flex;flex-direction:column;gap:7px}}
.gac-tag{{font-size:9px;font-weight:800;color:var(--pri);text-transform:uppercase;letter-spacing:2px}}
.gac-title{{font-size:15px;font-weight:700;line-height:1.35;color:var(--txt)}}
.gac-desc{{font-size:12px;color:var(--mut);line-height:1.7;flex:1}}
.gac-foot{{padding:0 20px 16px;display:flex;justify-content:space-between;align-items:center}}
.gac-date{{font-size:10px;color:var(--mut)}}
.gac-read{{font-size:12px;font-weight:800;color:var(--pri);display:flex;align-items:center;gap:4px;transition:gap .15s}}.gac:hover .gac-read{{gap:7px}}
/* author strip */
.gas{{background:var(--bg2);border-top:1px solid var(--brd);border-bottom:1px solid var(--brd);padding:40px 48px}}
.gas-inner{{max-width:760px;margin:0 auto;display:flex;gap:24px;align-items:center}}
.gas-avi{{width:64px;height:64px;border-radius:50%;background:var(--pri);display:flex;align-items:center;justify-content:center;font-size:20px;font-weight:800;color:#fff;flex-shrink:0;box-shadow:0 4px 12px rgba(249,115,22,.3)}}
.gas-bio p{{font-size:14px;color:var(--mut);line-height:1.75;margin-bottom:8px}}
.gas-link{{font-size:13px;font-weight:700;color:var(--pri);border-bottom:2px solid transparent;transition:border-color .15s}}.gas-link:hover{{border-bottom-color:var(--pri)}}
/* newsletter */
.gnl{{background:linear-gradient(135deg,var(--pri) 0%,var(--pri2) 100%);padding:80px 48px;text-align:center;position:relative;overflow:hidden}}
.gnl::before{{content:'';position:absolute;top:-80px;left:-80px;width:280px;height:280px;background:rgba(255,255,255,.07);border-radius:50%}}
.gnl::after{{content:'';position:absolute;bottom:-60px;right:-40px;width:200px;height:200px;background:rgba(255,255,255,.05);border-radius:50%}}
.gnl-inner{{position:relative}}
.gnl h2{{font-size:clamp(22px,3vw,38px);font-weight:800;color:#fff;margin-bottom:10px}}
.gnl p{{color:rgba(255,255,255,.88);font-size:15px;margin-bottom:32px}}
.gnl-form{{display:flex;gap:10px;max-width:460px;margin:0 auto;background:rgba(255,255,255,.15);border-radius:10px;padding:6px;backdrop-filter:blur(4px)}}
.gnl-input{{flex:1;border:none;border-radius:7px;padding:13px 16px;font-size:14px;outline:none;background:#fff;color:#111}}
.gnl-btn{{background:#000;color:#fff;border:none;border-radius:7px;padding:13px 24px;font-size:14px;font-weight:800;cursor:pointer;white-space:nowrap;transition:all .2s}}.gnl-btn:hover{{background:#111;transform:translateY(-1px)}}
/* footer */
.gft{{background:var(--txt);padding:40px 48px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:16px}}
.gft-brand{{font-size:16px;font-weight:800;color:var(--pri)}}
.gft-copy{{font-size:11px;color:rgba(255,255,255,.4);margin-top:4px}}
.gft-links{{display:flex;gap:20px}}.gft-links a{{font-size:12px;color:rgba(255,255,255,.5);transition:color .15s;text-decoration:none}}.gft-links a:hover{{color:#fff}}
/* mobile */
@media(max-width:1024px){{.gh-grid{{grid-template-columns:1fr}}.gv-grid{{grid-template-columns:repeat(2,1fr)}}}}
@media(max-width:768px){{.gn{{padding:0 16px}}.gn-links{{display:none}}.gh{{padding:36px 16px 32px}}.gt{{padding:14px 16px}}.gv{{padding:36px 16px}}.gaa{{padding:36px 16px}}.gq{{padding:40px 16px}}.gas{{padding:32px 16px}}.gnl{{padding:56px 16px}}.gnl-form{{flex-direction:column;background:none;padding:0}}.gnl-input{{border-radius:6px}}.gft{{padding:28px 16px;flex-direction:column;text-align:center}}}}
@media(max-width:480px){{.gv-grid{{grid-template-columns:1fr}}.gh-grid{{grid-template-columns:1fr}}}}
</style>
</head>
<body>

<nav class="gn">
  <div class="gn-logo">{s['name']}</div>
  <div class="gn-links">
    <a href="./">Home</a>
    <a href="about.html">About</a>
    <a href="#articles">Articles</a>
  </div>
  <button class="gn-cta" onclick="document.querySelector('.gnl').scrollIntoView({{behavior:'smooth'}})">Subscribe Free</button>
</nav>

<section class="gh">
  <div class="gh-eyebrow">{s['category']}</div>
  <h1 class="gh-h1">{s['tagline']}</h1>
  <p class="gh-sub">{s['hero_sub']}</p>
  <div class="gh-grid">
    <a id="gh-feat-link" href="#" class="gh-feat">
      <div class="gac-img-wrap"><img id="gh-feat-img" class="gh-feat-img" src="" alt=""></div>
      <div class="gh-feat-body">
        <div class="gh-feat-tag">{s['category']}</div>
        <div class="gh-feat-title" id="gh-feat-title">Loading featured article...</div>
        <div class="gh-feat-desc" id="gh-feat-desc"></div>
        <div class="gh-feat-meta" id="gh-feat-meta"></div>
      </div>
    </a>
    <div class="gh-side" id="gh-side"></div>
  </div>
</section>

<div class="gt">
  <span class="gt-label">Topics</span>
  <span class="gt-tag">Conversion Rate</span>
  <span class="gt-tag">AOV Growth</span>
  <span class="gt-tag">DTC Strategy</span>
  <span class="gt-tag">Shopify CRO</span>
  <span class="gt-tag">Email & SMS</span>
  <span class="gt-tag">Analytics</span>
  <span class="gt-tag">Checkout Optimization</span>
  <span class="gt-tag">Customer Retention</span>
</div>

<section class="gv reveal">
  <div class="gv-label">What You Get</div>
  <div class="gv-grid">
    <div class="gv-card">
      <div class="gv-icon">{ico_cart}</div>
      <div class="gv-head">Conversion Tactics</div>
      <div class="gv-body">Checkout and product page strategies grounded in 50+ real store audits  -  not generic best-practice lists.</div>
    </div>
    <div class="gv-card">
      <div class="gv-icon">{ico_trend}</div>
      <div class="gv-head">AOV & Revenue</div>
      <div class="gv-body">Bundling, upsell structures, and pricing frameworks that lift average order value without hurting CVR.</div>
    </div>
    <div class="gv-card">
      <div class="gv-icon">{ico_users}</div>
      <div class="gv-head">DTC Strategy</div>
      <div class="gv-body">The decisions that separate scaling DTC brands  -  from product-market fit signals to retention loops.</div>
    </div>
    <div class="gv-card">
      <div class="gv-icon">{ico_bar}</div>
      <div class="gv-head">Analytics & Data</div>
      <div class="gv-body">Metrics that actually predict revenue  -  not the vanity numbers most ecommerce dashboards show by default.</div>
    </div>
  </div>
</section>

<section class="gq reveal">
  <div class="gq-inner">
    <div class="gq-label">Daily Insight</div>
    <div class="gq-icon">{ico_quote}</div>
    <div class="gq-text" id="daily-insight-text">Loading today's insight...</div>
    <div class="gq-attr"> -  {s['author']}, {s['name']}</div>
  </div>
</section>

{_pexels_banner('200px', 'border-top:1px solid var(--brd);border-bottom:1px solid var(--brd);')}

<section class="gaa reveal" id="articles">
  <div class="gaa-hd">
    <span class="gaa-hd-text">All Articles</span>
  </div>
  <div class="gaa-grid" id="gaa-grid"></div>
</section>

<div class="gas reveal">
  <div class="gas-inner">
    <div class="gas-avi">{s['author'][0]}</div>
    <div class="gas-bio">
      <div style="font-size:15px;font-weight:700;color:var(--txt);margin-bottom:4px">{s['author']}</div>
      <div style="font-size:12px;color:var(--pri);font-weight:600;margin-bottom:8px">{s['author_title']}</div>
      <p>{s['bio1']}</p>
      <a href="about.html" class="gas-link">Full story →</a>
    </div>
  </div>
</div>

<section class="gnl">
  <div class="gnl-inner">
    <h2>{s['nl_head']}</h2>
    <p>{s['nl_sub']}</p>
    <form class="gnl-form" id="gnl-form" onsubmit="nlSub(event)">
      <input type="email" class="gnl-input" placeholder="your@email.com" required>
      <button type="submit" class="gnl-btn">Subscribe Free</button>
    </form>
  </div>
</section>

<footer class="gft">
  <div>
    <div class="gft-brand">{s['name']}</div>
    <div class="gft-copy">{s['footer_desc']}</div>
  </div>
  <div class="gft-links">
    <a href="./">Home</a><a href="about.html">About</a><a href="privacy.html">Privacy</a><a href="terms.html">Terms</a><a href="sms.html">SMS Policy</a><a href="meta-policy.html">Meta Policy</a>
  </div>
</footer>

<script>
const INSIGHTS=[
  "Most stores lose 70% of cart abandoners and never email them back the same day. That's the easiest win in ecommerce.",
  "Removing one unnecessary form field from checkout increases completion rate by an average of 4%. Audit yours this week.",
  "80% of Shopify revenue typically comes from 20% of SKUs. Know yours before running any paid acquisition.",
  "First-time customers who buy twice are 5x more likely to buy a third time. Your post-purchase flow determines which half they join.",
  "Hero images with lifestyle context outperform product-only images in 80% of A/B tests. Show the product in use.",
  "The average DTC brand spends 40% more acquiring customers than retaining them. That ratio should invert by year three.",
  "Set your free shipping threshold 15–20% above your current AOV. Not 5%, not 50%  -  and test it every quarter.",
  "Product page copy that addresses the top three objections before checkout outperforms generic 'buy now' pages by 2–3x.",
  "Abandoned cart emails sent within one hour recover 3x more revenue than those sent 24 hours later.",
  "Average mobile checkout abandonment is 85%. If you haven't audited your mobile experience this month, do it today.",
  "Subscription products with a 'pause' option have 40% lower churn than those with only a cancel option.",
  "Add social proof closest to the primary CTA  -  not in the header, not in the footer. Proximity matters.",
  "A 5% increase in customer retention produces more than a 25% increase in profit, on average.",
  "Post-purchase upsells convert at 3–5x the rate of pre-checkout upsells. Most stores haven't implemented either.",
];
const d=new Date();const idx=(d.getFullYear()*366+d.getMonth()*31+d.getDate())%INSIGHTS.length;
const el=document.getElementById('daily-insight-text');if(el)el.textContent=INSIGHTS[idx];

async function loadPosts(){{
  try{{
    const r=await fetch('./articles.json');if(!r.ok)throw 0;
    const posts=await r.json();if(!posts.length)throw 0;
    const feat=posts[0];
    const fl=document.getElementById('gh-feat-link');
    const fi=document.getElementById('gh-feat-img');
    if(fl)fl.href='./'+(feat.slug||'#')+'/';
    if(fi&&feat.image){{fi.src=feat.image;fi.alt=feat.title;}}
    const ft=document.getElementById('gh-feat-title');
    const fd=document.getElementById('gh-feat-desc');
    const fm=document.getElementById('gh-feat-meta');
    if(ft)ft.textContent=feat.title;
    if(fd)fd.textContent=(feat.meta_description||'').slice(0,130)+'...';
    if(fm)fm.textContent=feat.date_iso||'';
    const side=document.getElementById('gh-side');
    if(side)side.innerHTML=posts.slice(1,4).map(p=>`<a href="./${{p.slug||'#'}}/" class="gh-sub-art">${{p.image?`<div class="gac-img-wrap" style="width:88px;flex-shrink:0"><img class="gh-sub-img" src="${{p.image}}" alt="${{p.title}}" loading="lazy" style="width:88px;height:88px;object-fit:cover;display:block"></div>`:`<div class="gh-sub-img"></div>`}}<div class="gh-sub-body"><div class="gh-sub-tag">{s['category']}</div><div class="gh-sub-title">${{p.title}}</div><div class="gh-sub-date">${{p.date_iso||''}}</div></div></a>`).join('');
    const grid=document.getElementById('gaa-grid');
    if(grid)grid.innerHTML=posts.map(p=>`<a href="./${{p.slug||'#'}}/" class="gac"><div class="gac-img-wrap">${{p.image?`<img class="gac-img" src="${{p.image}}" alt="${{p.title}}" loading="lazy">`:`<div class="gac-img"></div>`}}</div><div class="gac-body"><div class="gac-tag">{s['category']}</div><div class="gac-title">${{p.title}}</div><div class="gac-desc">${{(p.meta_description||'').slice(0,110)}}...</div></div><div class="gac-foot"><span class="gac-date">${{p.date_iso||''}}</span><span class="gac-read">Read →</span></div></a>`).join('');
  }}catch(e){{
    const grid=document.getElementById('gaa-grid');
    if(grid)grid.innerHTML='<div class="gac"><div class="gac-body"><div class="gac-tag">Coming Soon</div><div class="gac-title">Articles publishing soon</div><div class="gac-desc">Check back shortly.</div></div></div>';
  }}
}}
function nlSub(e){{e.preventDefault();document.getElementById('gnl-form').innerHTML='<div style="color:#fff;font-size:16px;font-weight:600;padding:8px 0">Subscribed  -  first issue incoming.</div>';}}
const obs=new IntersectionObserver(entries=>entries.forEach(en=>{{if(en.isIntersecting){{en.target.classList.add('visible');obs.unobserve(en.target);}}}},{{threshold:.1}});
document.querySelectorAll('.reveal').forEach(el=>obs.observe(el));
loadPosts();
{_pexels_js(s)}
</script>
</body></html>"""


def grid_about(s):
    cv    = css_vars(s)
    ini   = ''.join(w[0] for w in s['author'].split() if w)
    story = _story_html(s, 'gab-p')
    pxjs  = _pexels_js(s)
    ico_conv  = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="9" cy="21" r="1"/><circle cx="20" cy="21" r="1"/><path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"/></svg>'
    ico_aov   = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>'
    ico_test  = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>'
    ico_ret   = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>'
    ico_data  = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>'
    ico_ckout = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/></svg>'
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>About {s['author']} - {s['name']}</title>
<meta name="description" content="{s['footer_desc']}">
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
:root{{{cv}}}
body{{font-family:var(--fb);background:var(--bg);color:var(--txt);font-size:15px;line-height:1.75}}
a{{color:var(--pri);text-decoration:none}}a:hover{{color:var(--pri2)}}
.gn{{background:#fff;border-bottom:2px solid var(--pri);padding:0 48px;display:flex;align-items:center;justify-content:space-between;height:62px;position:sticky;top:0;z-index:99;box-shadow:0 2px 12px rgba(0,0,0,.06)}}
.gn-logo{{font-size:19px;font-weight:800;color:var(--pri);letter-spacing:-.5px;text-decoration:none}}
.gn-links{{display:flex;gap:24px}}.gn-links a{{font-size:13px;color:var(--mut);font-weight:500;transition:color .2s}}.gn-links a:hover{{color:var(--pri)}}
/* hero */
.gab-hero{{background:var(--bg2);border-bottom:2px solid var(--pri);padding:48px 48px 40px}}
.gab-hero-top{{display:flex;align-items:center;gap:28px;margin-bottom:28px}}
.gab-avi{{width:80px;height:80px;border-radius:50%;background:var(--pri);display:flex;align-items:center;justify-content:center;font-size:26px;font-weight:800;color:#fff;flex-shrink:0;box-shadow:0 4px 16px rgba(249,115,22,.3)}}
.gab-hero h1{{font-size:clamp(22px,3vw,36px);font-weight:800;margin-bottom:4px;color:var(--txt)}}
.gab-hero-role{{font-size:14px;color:var(--pri);font-weight:700}}
.gab-hero-cat{{font-size:12px;color:var(--mut);margin-top:4px}}
.gab-stats{{display:flex;gap:14px;flex-wrap:wrap}}
.gab-stat{{background:#fff;border:1px solid var(--brd);border-radius:8px;padding:12px 18px;text-align:center;box-shadow:0 1px 4px rgba(0,0,0,.04)}}
.gab-stat-num{{font-size:22px;font-weight:800;color:var(--pri)}}
.gab-stat-lbl{{font-size:10px;color:var(--mut);margin-top:2px;text-transform:uppercase;letter-spacing:1px}}
/* layout */
.gab-layout{{display:grid;grid-template-columns:1fr 300px;gap:48px;max-width:1160px;margin:0 auto;padding:52px 48px}}
.gab-sec{{margin-bottom:44px}}
.gab-sec-hd{{font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:2px;color:var(--mut);border-bottom:1px solid var(--brd);padding-bottom:10px;margin-bottom:20px}}
.gab-p{{color:var(--mut);line-height:1.9;margin-bottom:16px;font-size:15px}}
/* expertise */
.gab-exp{{display:grid;grid-template-columns:1fr 1fr;gap:12px}}
.gab-exp-card{{border:1px solid var(--brd);border-radius:8px;padding:14px 16px;display:flex;gap:10px;align-items:flex-start;transition:border-color .2s,box-shadow .2s}}.gab-exp-card:hover{{border-color:var(--pri);box-shadow:0 3px 12px rgba(249,115,22,.08)}}
.gab-exp-icon{{color:var(--pri);flex-shrink:0;margin-top:1px}}
.gab-exp-head{{font-size:13px;font-weight:700;color:var(--txt);margin-bottom:3px}}
.gab-exp-body{{font-size:11px;color:var(--mut);line-height:1.6}}
/* methodology */
.gab-steps{{display:flex;flex-direction:column;gap:14px}}
.gab-step{{display:flex;gap:14px;align-items:flex-start}}
.gab-step-n{{width:30px;height:30px;border-radius:50%;background:var(--pri);color:#fff;font-size:12px;font-weight:800;display:flex;align-items:center;justify-content:center;flex-shrink:0}}
.gab-step-head{{font-size:14px;font-weight:700;color:var(--txt);margin-bottom:3px}}
.gab-step-body{{font-size:12px;color:var(--mut);line-height:1.65}}
/* sidebar */
.gab-side{{}}
.gab-card{{background:#fff;border:1px solid var(--brd);border-radius:10px;padding:22px;margin-bottom:18px;box-shadow:0 1px 6px rgba(0,0,0,.04)}}
.gab-card-lbl{{font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:2px;color:var(--pri);margin-bottom:12px}}
/* newsletter */
.gab-nl{{background:var(--pri);border-radius:10px;padding:24px;margin-bottom:18px;color:#fff}}
.gab-nl h3{{font-size:16px;font-weight:800;margin-bottom:6px}}
.gab-nl p{{font-size:12px;opacity:.88;margin-bottom:14px}}
.gab-nl-in{{width:100%;border:none;border-radius:6px;padding:10px 12px;font-size:13px;margin-bottom:8px;outline:none}}
.gab-nl-btn{{width:100%;background:#000;color:#fff;border:none;border-radius:6px;padding:10px;font-size:13px;font-weight:700;cursor:pointer;transition:opacity .2s}}.gab-nl-btn:hover{{opacity:.85}}
/* footer */
.gft{{background:var(--bg2);border-top:1px solid var(--brd);padding:28px 48px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px}}
.gft-copy{{font-size:12px;color:var(--mut)}}.gft-links{{display:flex;gap:20px}}.gft-links a{{font-size:12px;color:var(--mut);transition:color .15s}}.gft-links a:hover{{color:var(--pri)}}
@media(max-width:1024px){{.gab-layout{{grid-template-columns:1fr}}}}
@media(max-width:768px){{.gn{{padding:0 16px}}.gn-links{{display:none}}.gab-hero{{padding:32px 16px 28px}}.gab-hero-top{{flex-direction:column;gap:16px}}.gab-layout{{padding:32px 16px;gap:24px}}.gab-exp{{grid-template-columns:1fr}}.gft{{padding:20px 16px;flex-direction:column;text-align:center}}}}
</style>
</head>
<body>

<nav class="gn">
  <a href="./" class="gn-logo">{s['name']}</a>
  <div class="gn-links">
    <a href="./">Home</a>
    <a href="about.html">About</a>
  </div>
</nav>

<div class="gab-hero">
  <div class="gab-hero-top">
    <div class="gab-avi">{ini}</div>
    <div>
      <h1>{s['author']}</h1>
      <div class="gab-hero-role">{s['author_title']}</div>
      <div class="gab-hero-cat">{s['category']}</div>
    </div>
  </div>
  <div class="gab-stats">
    <div class="gab-stat"><div class="gab-stat-num">50+</div><div class="gab-stat-lbl">Stores Audited</div></div>
    <div class="gab-stat"><div class="gab-stat-num">8 Yrs</div><div class="gab-stat-lbl">In Ecommerce</div></div>
    <div class="gab-stat"><div class="gab-stat-num">$100M+</div><div class="gab-stat-lbl">GMV Analyzed</div></div>
    <div class="gab-stat"><div class="gab-stat-num">Independent</div><div class="gab-stat-lbl">No Vendor Ties</div></div>
  </div>
</div>

{_pexels_banner('200px', 'border-top:1px solid var(--brd);border-bottom:1px solid var(--brd);')}

<div class="gab-layout">

  <div class="gab-main">

    <div class="gab-sec">
      <div class="gab-sec-hd">Background</div>
      {story}
    </div>

    <div class="gab-sec">
      <div class="gab-sec-hd">Areas of Expertise</div>
      <div class="gab-exp">
        <div class="gab-exp-card">
          <div class="gab-exp-icon">{ico_conv}</div>
          <div><div class="gab-exp-head">Conversion Optimization</div><div class="gab-exp-body">Product page structure, checkout friction removal, and trust signal placement that move conversion rates.</div></div>
        </div>
        <div class="gab-exp-card">
          <div class="gab-exp-icon">{ico_aov}</div>
          <div><div class="gab-exp-head">AOV & Revenue Growth</div><div class="gab-exp-body">Post-purchase upsells, bundle architecture, and pricing strategies that lift average order value.</div></div>
        </div>
        <div class="gab-exp-card">
          <div class="gab-exp-icon">{ico_test}</div>
          <div><div class="gab-exp-head">A/B Testing Frameworks</div><div class="gab-exp-body">Structuring experiments that produce valid results  -  not the underpowered tests that fill most CRO reports.</div></div>
        </div>
        <div class="gab-exp-card">
          <div class="gab-exp-icon">{ico_ret}</div>
          <div><div class="gab-exp-head">Customer Retention</div><div class="gab-exp-body">Email flows, LTV segmentation, and the post-purchase experience that turns first buyers into repeat customers.</div></div>
        </div>
        <div class="gab-exp-card">
          <div class="gab-exp-icon">{ico_data}</div>
          <div><div class="gab-exp-head">Analytics & Attribution</div><div class="gab-exp-body">Setting up measurement that actually reflects what's driving revenue  -  not what's easiest to track.</div></div>
        </div>
        <div class="gab-exp-card">
          <div class="gab-exp-icon">{ico_ckout}</div>
          <div><div class="gab-exp-head">Checkout & Funnel</div><div class="gab-exp-body">Reducing drop-off at every stage of the purchase path from landing page through order confirmation.</div></div>
        </div>
      </div>
    </div>

    <div class="gab-sec">
      <div class="gab-sec-hd">How I Approach a Store Audit</div>
      <div class="gab-steps">
        <div class="gab-step"><div class="gab-step-n">1</div><div><div class="gab-step-head">Traffic & Source Analysis</div><div class="gab-step-body">Understand where buyers come from, what they expect when they arrive, and how well the landing experience matches that expectation.</div></div></div>
        <div class="gab-step"><div class="gab-step-n">2</div><div><div class="gab-step-head">Product Page Review</div><div class="gab-step-body">Evaluate information hierarchy, image quality, trust signals, objection handling, and call-to-action clarity against what actually drives add-to-cart.</div></div></div>
        <div class="gab-step"><div class="gab-step-n">3</div><div><div class="gab-step-head">Cart & Checkout Mapping</div><div class="gab-step-body">Identify every point of friction between add-to-cart and completed purchase  -  form fields, payment options, shipping clarity, and mobile experience.</div></div></div>
        <div class="gab-step"><div class="gab-step-n">4</div><div><div class="gab-step-head">Post-Purchase & Retention</div><div class="gab-step-body">Assess how well the brand captures repeat purchase intent, upsells at confirmation, and sets up email flows for LTV growth.</div></div></div>
        <div class="gab-step"><div class="gab-step-n">5</div><div><div class="gab-step-head">Prioritized Recommendations</div><div class="gab-step-body">Rank findings by expected impact and implementation cost. Most stores have three or four high-leverage changes and a long tail of minor improvements.</div></div></div>
      </div>
    </div>

    <div class="gab-sec">
      <div class="gab-sec-hd">About {s['name']}</div>
      <p class="gab-p">{s['hero_sub']}</p>
      <p class="gab-p">{s['footer_desc']}</p>
    </div>

    <div class="gab-sec">
      <div class="gab-sec-hd">Contributors</div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px">
        {_contributors_html(s,'var(--bg2)','var(--brd)','var(--txt)','var(--mut)','var(--pri)')}
      </div>
    </div>

    <div class="gab-sec">
      <div class="gab-sec-hd">Reader Comments</div>
      <div style="background:var(--bg2);border:1px solid var(--brd);border-radius:10px;padding:4px 20px">
        {_comments_html(s,'var(--bg2)','var(--brd)','var(--txt)','var(--mut)','var(--pri)')}
      </div>
    </div>

  </div>

  <aside class="gab-side">

    <div class="gab-nl">
      <h3>{s['nl_head']}</h3>
      <p>{s['nl_sub']}</p>
      <form id="gab-nl-form" onsubmit="nlSub(event)">
        <input type="email" class="gab-nl-in" placeholder="your@email.com" required>
        <button type="submit" class="gab-nl-btn">Subscribe</button>
      </form>
    </div>

    <div class="gab-card">
      <div class="gab-card-lbl">Credentials</div>
      <p style="font-size:13px;color:var(--mut);line-height:1.8;margin-bottom:8px">{s['author_title']}</p>
      <p style="font-size:13px;color:var(--mut);line-height:1.8">Independent consultant. No platform sponsorships. No affiliated tools.</p>
    </div>

    <div class="gab-card">
      <div class="gab-card-lbl">Focus Topics</div>
      <ul style="list-style:none;display:flex;flex-direction:column;gap:8px">
        <li style="font-size:13px;color:var(--mut);display:flex;align-items:center;gap:8px"><span style="color:var(--pri);font-weight:700">→</span> Shopify CRO</li>
        <li style="font-size:13px;color:var(--mut);display:flex;align-items:center;gap:8px"><span style="color:var(--pri);font-weight:700">→</span> DTC Growth Strategy</li>
        <li style="font-size:13px;color:var(--mut);display:flex;align-items:center;gap:8px"><span style="color:var(--pri);font-weight:700">→</span> Paid Acquisition</li>
        <li style="font-size:13px;color:var(--mut);display:flex;align-items:center;gap:8px"><span style="color:var(--pri);font-weight:700">→</span> Email & SMS Revenue</li>
        <li style="font-size:13px;color:var(--mut);display:flex;align-items:center;gap:8px"><span style="color:var(--pri);font-weight:700">→</span> Post-Purchase UX</li>
      </ul>
    </div>

    <div class="gab-card" id="gab-recent">
      <div class="gab-card-lbl">Recent Articles</div>
      <div id="gab-recent-list" style="display:flex;flex-direction:column;gap:10px"></div>
    </div>

  </aside>
</div>

<footer class="gft">
  <span class="gft-copy">© {s['name']}</span>
  <div class="gft-links">
    <a href="./">Home</a><a href="about.html">About</a><a href="privacy.html">Privacy Policy</a><a href="terms.html">Terms</a><a href="sms.html">SMS Policy</a><a href="meta-policy.html">Meta Policy</a>
  </div>
</footer>

<script>
function nlSub(e){{e.preventDefault();document.getElementById('gab-nl-form').innerHTML='<div style="color:#fff;font-weight:600;padding:6px 0">Subscribed  -  first issue incoming.</div>';}}
async function loadRecent(){{
  try{{
    const r=await fetch('./articles.json');if(!r.ok)return;
    const posts=await r.json();
    const el=document.getElementById('gab-recent-list');
    if(el)el.innerHTML=posts.slice(0,4).map(p=>`<a href="./${{p.slug||'#'}}/" style="text-decoration:none;color:inherit;display:block"><div style="border-bottom:1px solid var(--brd);padding-bottom:8px"><div style="font-size:9px;color:var(--pri);font-weight:700;text-transform:uppercase;letter-spacing:1px;margin-bottom:3px">{s['category']}</div><div style="font-size:13px;font-weight:600;color:var(--txt);line-height:1.4">${{p.title}}</div><div style="font-size:10px;color:var(--mut);margin-top:3px">${{p.date_iso||''}}</div></div></a>`).join('');
  }}catch(e){{}}
}}
loadRecent();
{pxjs}
</script>
</body></html>"""


# ── TEMPLATE: LEAF (warm editorial) ───────────────────────────────────────────
def leaf_index(s):
    cv = css_vars(s)
    nm = s['name'].split()
    nm_first = nm[0]
    nm_rest  = ' '.join(nm[1:])
    ico_trend  = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>'
    ico_dollar = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>'
    ico_pie    = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21.21 15.89A10 10 0 1 1 8 2.83"/><path d="M22 12A10 10 0 0 0 12 2v10z"/></svg>'
    ico_shield = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>'
    ico_home   = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>'
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{s['name']} - {s['tagline']}</title>
<meta name="description" content="{s['hero_sub']}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Lora:wght@400;600;700&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
:root{{{cv}--fh:Lora,Georgia,serif;}}
body{{font-family:var(--fb);background:var(--bg);color:var(--txt);font-size:15px;line-height:1.78}}
a{{color:var(--pri);text-decoration:none}}a:hover{{text-decoration:underline}}
/* nav */
.ln{{display:flex;align-items:center;justify-content:space-between;padding:18px 52px;border-bottom:1px solid var(--brd);background:var(--bg);position:sticky;top:0;z-index:99}}
.ln-brand{{font-family:var(--fh);font-size:22px;font-weight:700;color:var(--txt);text-decoration:none;letter-spacing:-.3px}}
.ln-brand em{{color:var(--pri);font-style:normal}}
.ln-nav{{display:flex;gap:28px}}.ln-nav a{{font-size:13px;color:var(--mut);font-weight:500;transition:color .2s;text-decoration:none}}.ln-nav a:hover{{color:var(--txt)}}
/* hero */
.lh{{background:var(--bg2);border-bottom:2px solid var(--brd);padding:64px 52px 52px}}
.lh-eyebrow{{font-size:11px;font-weight:700;color:var(--pri);text-transform:uppercase;letter-spacing:3px;margin-bottom:18px}}
.lh-h1{{font-family:var(--fh);font-size:clamp(28px,4vw,52px);font-weight:700;line-height:1.1;max-width:660px;margin-bottom:18px;color:var(--txt)}}
.lh-sub{{color:var(--mut);font-size:16px;max-width:560px;line-height:1.9;margin-bottom:28px}}
.lh-stats{{display:flex;gap:0;border:1px solid var(--brd);border-radius:8px;overflow:hidden;max-width:480px;background:#fff}}
.lh-stat{{flex:1;padding:14px 18px;text-align:center;border-right:1px solid var(--brd)}}.lh-stat:last-child{{border-right:none}}
.lh-stat-num{{font-family:var(--fh);font-size:20px;font-weight:700;color:var(--pri)}}
.lh-stat-lbl{{font-size:10px;color:var(--mut);margin-top:2px;text-transform:uppercase;letter-spacing:1px}}
/* pillars */
.lp{{padding:0 52px;border-bottom:1px solid var(--brd);background:var(--bg)}}
.lp-inner{{display:flex;align-items:stretch;overflow-x:auto;gap:0;max-width:1200px;margin:0 auto}}
.lp-item{{display:flex;align-items:center;gap:8px;padding:14px 20px;font-size:13px;font-weight:600;color:var(--mut);border-right:1px solid var(--brd);white-space:nowrap;transition:color .2s,background .2s;cursor:default}}.lp-item:first-child{{border-left:none}}.lp-item:hover{{color:var(--pri);background:var(--bg2);text-decoration:none}}
.lp-icon{{color:var(--pri);flex-shrink:0}}
/* featured article */
.lf-feat{{padding:52px 52px 0;max-width:1200px;margin:0 auto}}
.lf-feat-hd{{font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:2px;color:var(--mut);margin-bottom:20px;padding-bottom:10px;border-bottom:2px solid var(--brd)}}
.lf-feat-card{{display:grid;grid-template-columns:1fr 380px;gap:0;border:1px solid var(--brd);border-radius:10px;overflow:hidden;background:var(--bg2);transition:box-shadow .2s;text-decoration:none;color:inherit}}.lf-feat-card:hover{{box-shadow:0 8px 32px rgba(0,0,0,.08);text-decoration:none}}
.lf-feat-img{{width:100%;height:320px;object-fit:cover;display:block;background:var(--sur)}}
.lf-feat-body{{padding:32px 32px;display:flex;flex-direction:column;justify-content:center}}
.lf-feat-label{{font-size:10px;font-weight:700;color:var(--pri);text-transform:uppercase;letter-spacing:2px;margin-bottom:14px}}
.lf-feat-title{{font-family:var(--fh);font-size:clamp(18px,2.5vw,26px);font-weight:700;line-height:1.3;color:var(--txt);margin-bottom:14px}}
.lf-feat-desc{{font-size:14px;color:var(--mut);line-height:1.8;margin-bottom:18px}}
.lf-feat-meta{{font-size:11px;color:var(--mut);margin-bottom:20px}}
.lf-feat-read{{display:inline-block;border:2px solid var(--pri);color:var(--pri);padding:9px 22px;border-radius:5px;font-size:13px;font-weight:700;transition:all .15s}}.lf-feat-read:hover{{background:var(--pri);color:#fff;text-decoration:none}}
/* stream */
.ls{{padding:40px 52px 52px;max-width:1200px;margin:0 auto}}
.ls-hd{{font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:2px;color:var(--mut);margin-bottom:28px;padding-bottom:10px;border-bottom:1px solid var(--brd)}}
.ls-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:26px}}
.ls-post{{background:var(--bg2);border-radius:10px;overflow:hidden;border:1px solid var(--brd);display:flex;flex-direction:column;transition:box-shadow .2s;text-decoration:none;color:inherit}}.ls-post:hover{{box-shadow:0 6px 24px rgba(0,0,0,.07);text-decoration:none}}
.ls-post-img{{width:100%;height:190px;object-fit:cover;display:block;background:var(--sur)}}
.ls-post-body{{padding:20px 22px 16px;flex:1;display:flex;flex-direction:column;gap:8px}}
.ls-post-label{{font-size:10px;font-weight:700;color:var(--pri);text-transform:uppercase;letter-spacing:2px}}
.ls-post-title{{font-family:var(--fh);font-size:16px;font-weight:700;line-height:1.35;color:var(--txt)}}
.ls-post-desc{{font-size:13px;color:var(--mut);line-height:1.75;flex:1}}
.ls-post-foot{{padding:0 22px 18px;display:flex;justify-content:space-between;align-items:center}}
.ls-post-date{{font-size:11px;color:var(--mut)}}
.ls-post-link{{font-size:13px;font-weight:600;color:var(--pri)}}
/* value props */
.lvp{{padding:40px 52px;border-bottom:1px solid var(--brd);background:var(--bg2)}}
.lvp-inner{{max-width:1200px;margin:0 auto;display:grid;grid-template-columns:repeat(3,1fr);gap:20px}}
.lvp-card{{background:var(--bg);border:1px solid var(--brd);border-radius:10px;padding:24px}}
.lvp-icon{{width:40px;height:40px;border-radius:8px;background:var(--pri)1a;display:flex;align-items:center;justify-content:center;color:var(--pri);margin-bottom:12px}}
.lvp-title{{font-family:var(--fh);font-size:16px;font-weight:700;color:var(--txt);margin-bottom:6px}}
.lvp-desc{{font-size:13px;color:var(--mut);line-height:1.75}}
/* author note */
.lan{{padding:40px 52px;border-top:1px solid var(--brd);border-bottom:1px solid var(--brd);background:var(--bg2)}}
.lan-inner{{max-width:1200px;margin:0 auto;display:grid;grid-template-columns:80px 1fr;gap:24px;align-items:center}}
.lan-av{{width:72px;height:72px;border-radius:50%;background:var(--pri);display:flex;align-items:center;justify-content:center;font-family:var(--fh);font-size:22px;font-weight:700;color:#fff;flex-shrink:0}}
.lan-name{{font-family:var(--fh);font-size:18px;font-weight:700;color:var(--txt);margin-bottom:2px}}
.lan-role{{font-size:12px;color:var(--pri);font-weight:600;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px}}
.lan-bio{{font-size:14px;color:var(--mut);line-height:1.75}}
.lan-link{{display:inline-block;margin-top:10px;font-size:13px;font-weight:600;color:var(--pri);border-bottom:1px solid var(--pri);text-decoration:none}}
/* newsletter */
.lnl{{background:var(--pri);padding:72px 52px;display:flex;gap:64px;align-items:center}}
.lnl-text{{flex:1}}
.lnl-text h2{{font-family:var(--fh);font-size:clamp(22px,3vw,34px);font-weight:700;color:#fff;margin-bottom:10px;line-height:1.2}}
.lnl-text p{{color:rgba(255,255,255,.85);font-size:15px;line-height:1.75}}
.lnl-form-wrap{{flex-shrink:0;width:360px}}
.lnl-form-sub{{color:rgba(255,255,255,.85);font-size:13px;margin-bottom:12px}}
.lnl-in{{width:100%;border:none;border-radius:6px;padding:12px 14px;font-size:14px;outline:none;margin-bottom:10px;background:rgba(255,255,255,.95)}}
.lnl-btn{{width:100%;background:#000;color:#fff;border:none;border-radius:6px;padding:12px;font-size:14px;font-weight:700;cursor:pointer;transition:opacity .2s}}.lnl-btn:hover{{opacity:.85}}
/* footer */
.lfb{{padding:24px 52px;border-top:1px solid var(--brd);display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px}}
.lfb-copy{{font-size:12px;color:var(--mut)}}
.lfb-links{{display:flex;gap:20px}}.lfb-links a{{font-size:12px;color:var(--mut);text-decoration:none}}.lfb-links a:hover{{color:var(--pri)}}
@media(max-width:1024px){{.lf-feat-card{{grid-template-columns:1fr}}}}
@media(max-width:768px){{.ln{{padding:14px 16px}}.lh{{padding:40px 16px 32px}}.lp{{padding:0 16px}}.lf-feat{{padding:36px 16px 0}}.ls{{padding:32px 16px 40px}}.lnl{{flex-direction:column;padding:52px 16px;gap:32px}}.lnl-form-wrap{{width:100%}}.lfb{{padding:20px 16px;flex-direction:column;text-align:center}}.lvp{{padding:32px 16px}}.lvp-inner{{grid-template-columns:1fr}}.lan{{padding:32px 16px}}.lan-inner{{grid-template-columns:1fr}}}}
</style>
</head>
<body>

<nav class="ln">
  <a href="./" class="ln-brand">{nm_first} <em>{nm_rest}</em></a>
  <nav class="ln-nav">
    <a href="./">Home</a>
    <a href="about.html">About</a>
    <a href="#articles">Articles</a>
  </nav>
</nav>

<div class="lh">
  <div class="lh-eyebrow">{s['category']}</div>
  <h1 class="lh-h1">{s['tagline']}</h1>
  <p class="lh-sub">{s['hero_sub']}</p>
  <div class="lh-stats">
    {"".join(f'<div class="lh-stat"><div class="lh-stat-num">{st[0]}</div><div class="lh-stat-lbl">{st[1]}</div></div>' for st in s.get("leaf_stats",[("15+","Yrs Investing"),("CFP","Certified"),("41","Retired At")]))}
  </div>
</div>

<div class="lp">
  <div class="lp-inner">
    {"".join(f'<div class="lp-item"><span class="lp-icon">{ico_trend}</span> {p}</div>' for p in s.get("leaf_pillars",["Dividend Investing","REITs","Index Funds","Tax Strategy","Risk Management"]))}
  </div>
</div>

<div class="lvp">
  <div class="lvp-inner">
    {"".join(f'<div class="lvp-card"><div class="lvp-icon">{[ico_trend,ico_dollar,ico_shield][i%3]}</div><div class="lvp-title">{vp[0]}</div><div class="lvp-desc">{vp[1]}</div></div>' for i,vp in enumerate(s.get("leaf_vp",[("Real Numbers, Real Timelines","Every strategy includes honest math: how long it takes, what capital you need, and what taxes look like."),("Multiple Income Streams","Dividends, REITs, index funds, rental income - layer passive income streams that compound over time."),("Expert-Verified Guidance","Written by a certified planner with lived experience. Not theory - real numbers.")])))}
  </div>
</div>

{_pexels_banner('220px', 'border-top:1px solid var(--brd);border-bottom:1px solid var(--brd);')}

<div class="lf-feat">
  <div class="lf-feat-hd">Featured</div>
  <a id="lf-feat-link" href="#" class="lf-feat-card">
    <img id="lf-feat-img" class="lf-feat-img" src="" alt="">
    <div class="lf-feat-body">
      <div class="lf-feat-label">{s['category']}</div>
      <div class="lf-feat-title" id="lf-feat-title">Loading...</div>
      <div class="lf-feat-desc" id="lf-feat-desc"></div>
      <div class="lf-feat-meta" id="lf-feat-meta"></div>
      <div class="lf-feat-read">Read article</div>
    </div>
  </a>
</div>

<div class="ls" id="articles">
  <div class="ls-hd">All Articles</div>
  <div class="ls-grid" id="ls-grid"></div>
</div>

<div class="lan">
  <div class="lan-inner">
    <div class="lan-av">{''.join(w[0] for w in s['author'].split()[:2])}</div>
    <div>
      <div class="lan-name">{s['author']}</div>
      <div class="lan-role">{s['author_title']}</div>
      <div class="lan-bio">{s['bio1']}</div>
      <a href="about.html" class="lan-link">Read full story and methodology</a>
    </div>
  </div>
</div>

<div class="lnl">
  <div class="lnl-text">
    <h2>{s['nl_head']}</h2>
    <p>Written by {s['author']}, {s['author_title'].lower()}. {s.get('footer_desc','Expert analysis and practical guides, free every month.')}</p>
  </div>
  <div class="lnl-form-wrap">
    <div class="lnl-form-sub">{s['nl_sub']}</div>
    <form id="lnl-form" onsubmit="nlSub(event)">
      <input type="email" class="lnl-in" placeholder="your@email.com" required>
      <button type="submit" class="lnl-btn">Join the letter</button>
    </form>
  </div>
</div>

<div class="lfb">
  <span class="lfb-copy">© {s['name']} · {s['footer_desc']}</span>
  <div class="lfb-links">
    <a href="./">Home</a><a href="about.html">About</a><a href="privacy.html">Privacy Policy</a><a href="terms.html">Terms</a><a href="sms.html">SMS Policy</a><a href="meta-policy.html">Meta Policy</a>
  </div>
</div>

<script>
function clean(t){{return (t||'').replace(/ - /g,'...').replace(/–/g,'-').trim();}}
async function loadPosts(){{
  try{{
    const r=await fetch('./articles.json');if(!r.ok)throw 0;
    const posts=await r.json();if(!posts.length)throw 0;
    const feat=posts[0];
    const fl=document.getElementById('lf-feat-link');
    const fi=document.getElementById('lf-feat-img');
    if(fl)fl.href='./'+(feat.slug||'#')+'/';
    if(fi&&feat.image){{fi.src=feat.image;fi.alt=clean(feat.title);}}
    const ft=document.getElementById('lf-feat-title');
    const fd=document.getElementById('lf-feat-desc');
    const fm=document.getElementById('lf-feat-meta');
    if(ft)ft.textContent=clean(feat.title);
    if(fd)fd.textContent=clean(feat.meta_description).slice(0,160);
    if(fm)fm.textContent=feat.date_iso||'';
    const grid=document.getElementById('ls-grid');
    if(grid)grid.innerHTML=posts.map(function(p){{
      return '<a href="./'+p.slug+'/" class="ls-post">'+(p.image?'<img class="ls-post-img" src="'+p.image+'" alt="'+clean(p.title)+'" loading="lazy">':'<div class="ls-post-img" style="background:var(--bg2)"></div>')+'<div class="ls-post-body"><div class="ls-post-label">{s['category']}</div><div class="ls-post-title">'+clean(p.title)+'</div><div class="ls-post-desc">'+clean(p.meta_description).slice(0,130)+'</div></div><div class="ls-post-foot"><span class="ls-post-date">'+(p.date_iso||'')+'</span><span class="ls-post-link">Read article</span></div></a>';
    }}).join('');
  }}catch(e){{
    const grid=document.getElementById('ls-grid');
    if(grid)grid.innerHTML='<div class="ls-post"><div class="ls-post-body"><div class="ls-post-label">Coming Soon</div><div class="ls-post-title">Articles publishing soon</div><div class="ls-post-desc">Check back shortly.</div></div></div>';
  }}
}}
function nlSub(e){{e.preventDefault();document.getElementById('lnl-form').innerHTML='<div style="color:#fff;font-size:15px;font-weight:600;padding:8px 0">Welcome to the letter.</div>';}}
loadPosts();
{_pexels_js(s)}
</script>
</body></html>"""


def leaf_about(s):
    cv    = css_vars(s)
    ini   = ''.join(w[0] for w in s['author'].split() if w)
    story = _story_html(s, 'la-p')
    pxjs  = _pexels_js(s)
    nm    = s['name'].split()
    nm_first = nm[0]
    nm_rest  = ' '.join(nm[1:])
    ico_trend  = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>'
    ico_dollar = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>'
    ico_pie    = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M21.21 15.89A10 10 0 1 1 8 2.83"/><path d="M22 12A10 10 0 0 0 12 2v10z"/></svg>'
    ico_shield = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>'
    ico_home   = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>'
    ico_cal    = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>'
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>About {s['author']} - {s['name']}</title>
<meta name="description" content="{s['footer_desc']}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Lora:wght@400;600;700&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
:root{{{cv}--fh:Lora,Georgia,serif;}}
body{{font-family:var(--fb);background:var(--bg);color:var(--txt);font-size:15px;line-height:1.8}}
a{{color:var(--pri);text-decoration:none}}a:hover{{text-decoration:underline}}
.ln{{display:flex;align-items:center;justify-content:space-between;padding:18px 52px;border-bottom:1px solid var(--brd);background:var(--bg);position:sticky;top:0;z-index:99}}
.ln-brand{{font-family:var(--fh);font-size:22px;font-weight:700;color:var(--txt);text-decoration:none}}
.ln-brand em{{color:var(--pri);font-style:normal}}
.ln-nav{{display:flex;gap:28px}}.ln-nav a{{font-size:13px;color:var(--mut);font-weight:500;text-decoration:none}}.ln-nav a:hover{{color:var(--txt)}}
/* hero */
.lah{{background:var(--bg2);border-bottom:2px solid var(--brd);padding:52px 52px 44px}}
.lah-top{{display:flex;align-items:center;gap:32px;margin-bottom:28px}}
.lah-avi{{width:80px;height:80px;border-radius:50%;background:var(--pri);display:flex;align-items:center;justify-content:center;font-family:var(--fh);font-size:26px;font-weight:700;color:#fff;flex-shrink:0;border:3px solid var(--bg)}}
.lah h1{{font-family:var(--fh);font-size:clamp(22px,3vw,36px);font-weight:700;margin-bottom:4px;color:var(--txt)}}
.lah-role{{font-size:14px;color:var(--pri);font-weight:600}}
.lah-cat{{font-size:12px;color:var(--mut);margin-top:4px}}
.lah-stats{{display:flex;gap:14px;flex-wrap:wrap}}
.lah-stat{{background:var(--bg);border:1px solid var(--brd);border-radius:8px;padding:12px 18px;text-align:center}}
.lah-stat-num{{font-family:var(--fh);font-size:20px;font-weight:700;color:var(--pri)}}
.lah-stat-lbl{{font-size:10px;color:var(--mut);margin-top:2px;text-transform:uppercase;letter-spacing:1px}}
/* layout */
.la-layout{{display:grid;grid-template-columns:1fr 300px;gap:48px;max-width:1160px;margin:0 auto;padding:52px 52px}}
.la-sec{{margin-bottom:44px}}
.la-sec-hd{{font-family:var(--fh);font-size:20px;font-weight:700;color:var(--txt);margin-bottom:16px;padding-bottom:12px;border-bottom:2px solid var(--pri)}}
.la-p{{color:var(--mut);line-height:1.9;margin-bottom:16px}}
/* quote */
.la-quote{{border-left:3px solid var(--pri);padding:12px 20px;margin:4px 0 24px;background:var(--bg2);border-radius:0 6px 6px 0}}
.la-quote p{{font-family:var(--fh);font-size:16px;color:var(--txt);line-height:1.7;font-style:italic}}
/* invest grid */
.la-inv{{display:grid;grid-template-columns:1fr 1fr;gap:12px}}
.la-inv-card{{border:1px solid var(--brd);border-radius:8px;padding:14px 16px;display:flex;gap:10px;align-items:flex-start;transition:border-color .2s}}.la-inv-card:hover{{border-color:var(--pri)}}
.la-inv-icon{{color:var(--pri);flex-shrink:0;margin-top:2px}}
.la-inv-head{{font-size:13px;font-weight:700;color:var(--txt);margin-bottom:3px}}
.la-inv-body{{font-size:12px;color:var(--mut);line-height:1.65}}
/* journey timeline */
.laj{{padding:44px 52px;border-bottom:1px solid var(--brd);background:var(--bg2)}}
.laj-inner{{max-width:1160px;margin:0 auto}}
.laj-hd{{font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:3px;color:var(--mut);margin-bottom:28px}}
.laj-items{{display:grid;grid-template-columns:repeat(5,1fr);gap:0;position:relative}}
.laj-items::before{{content:'';position:absolute;top:12px;left:0;right:0;height:2px;background:var(--brd);z-index:0}}
.laj-item{{display:flex;flex-direction:column;gap:8px;padding-top:0;position:relative;z-index:1;padding-right:14px}}
.laj-dot{{width:26px;height:26px;border-radius:50%;background:var(--pri);border:3px solid var(--bg2);flex-shrink:0}}
.laj-year{{font-family:var(--fh);font-size:13px;font-weight:700;color:var(--pri);margin-top:4px}}
.laj-text{{font-size:12px;color:var(--mut);line-height:1.65}}
/* philosophy banner */
.la-philo{{background:var(--pri);padding:40px 52px;text-align:center;border-top:1px solid rgba(0,0,0,.1)}}
.la-philo blockquote{{font-family:var(--fh);font-size:clamp(16px,2.2vw,22px);font-style:italic;color:#fff;max-width:760px;margin:0 auto;line-height:1.6}}
.la-philo cite{{display:block;margin-top:12px;font-size:11px;color:rgba(255,255,255,.7);font-style:normal;letter-spacing:1.5px;text-transform:uppercase}}
/* methodology */
.la-steps{{display:flex;flex-direction:column;gap:16px}}
.la-step{{display:flex;gap:14px}}
.la-step-dot{{width:28px;height:28px;border-radius:50%;background:var(--pri);color:#fff;font-size:12px;font-weight:800;display:flex;align-items:center;justify-content:center;flex-shrink:0;margin-top:2px}}
.la-step-head{{font-family:var(--fh);font-size:15px;font-weight:700;color:var(--txt);margin-bottom:4px}}
.la-step-body{{font-size:13px;color:var(--mut);line-height:1.7}}
/* sidebar */
.la-side{{}}
.la-card{{background:var(--bg2);border:1px solid var(--brd);border-radius:10px;padding:22px;margin-bottom:18px}}
.la-card-lbl{{font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:2px;color:var(--pri);margin-bottom:12px}}
/* nl */
.la-nl{{background:var(--pri);border-radius:10px;padding:24px;margin-bottom:18px;color:#fff}}
.la-nl h3{{font-family:var(--fh);font-size:18px;font-weight:700;margin-bottom:6px}}
.la-nl p{{font-size:12px;opacity:.88;margin-bottom:14px}}
.la-nl-in{{width:100%;border:none;border-radius:6px;padding:10px 12px;font-size:13px;margin-bottom:8px;outline:none;background:rgba(255,255,255,.95)}}
.la-nl-btn{{width:100%;background:#1c1a14;color:#fff;border:none;border-radius:6px;padding:10px;font-size:13px;font-weight:700;cursor:pointer;transition:opacity .2s}}.la-nl-btn:hover{{opacity:.85}}
/* footer */
.lfb{{padding:24px 52px;border-top:1px solid var(--brd);display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px}}
.lfb-copy{{font-size:12px;color:var(--mut)}}.lfb-links{{display:flex;gap:20px}}.lfb-links a{{font-size:12px;color:var(--mut);text-decoration:none}}.lfb-links a:hover{{color:var(--pri)}}
@media(max-width:1024px){{.la-layout{{grid-template-columns:1fr}}}}
@media(max-width:768px){{.ln{{padding:14px 16px}}.lah{{padding:32px 16px 28px}}.lah-top{{flex-direction:column;gap:16px}}.la-layout{{padding:32px 16px;gap:28px}}.la-inv{{grid-template-columns:1fr}}.laj{{padding:32px 16px}}.laj-items{{grid-template-columns:1fr 1fr;gap:24px}}.laj-items::before{{display:none}}.la-philo{{padding:32px 16px}}.lfb{{padding:20px 16px;flex-direction:column;text-align:center}}}}
</style>
</head>
<body>

<nav class="ln">
  <a href="./" class="ln-brand">{nm_first} <em>{nm_rest}</em></a>
  <nav class="ln-nav">
    <a href="./">Home</a>
    <a href="about.html">About</a>
  </nav>
</nav>

<div class="lah">
  <div class="lah-top">
    <div class="lah-avi">{ini}</div>
    <div>
      <h1>{s['author']}</h1>
      <div class="lah-role">{s['author_title']}</div>
      <div class="lah-cat">{s['category']}</div>
    </div>
  </div>
  <div class="lah-stats">
    {"".join(f'<div class="lah-stat"><div class="lah-stat-num">{st[0]}</div><div class="lah-stat-lbl">{st[1]}</div></div>' for st in s.get("leaf_stats",[("15+","Yrs Investing"),("CFP","Certified"),("Retired 41","Passive Income"),("4","Income Streams")]))}
  </div>
</div>

{_pexels_banner('220px', 'border-top:1px solid var(--brd);border-bottom:1px solid var(--brd);')}

<!-- JOURNEY TIMELINE -->
<div class="laj">
  <div class="laj-inner">
    <div class="laj-hd">The Journey</div>
    <div class="laj-items">
      {"".join(f'<div class="laj-item"><div class="laj-dot"></div><div class="laj-year">{jt[0]}</div><div class="laj-text">{jt[1]}</div></div>' for jt in s.get("leaf_journey",[("Age 26","Opened first brokerage account. Started with index funds and small monthly contributions."),("Age 30","First dividend payment. Small, but proof the strategy was real."),("Age 35","CFP designation earned. Passive income crossed $1,000/month for the first time."),("Age 39","Launched a digital product. Added a fourth income stream without adding working hours."),("Age 41","Financial independence reached. Left traditional employment.")]))}
    </div>
  </div>
</div>

<!-- PHILOSOPHY BANNER -->
<div class="la-philo">
  <blockquote>"{s['tagline']}"</blockquote>
  <cite>{s['author']} · {s['author_title']}</cite>
</div>

<div class="la-layout">

  <div class="la-main">

    <div class="la-sec">
      <div class="la-sec-hd">Background</div>
      {story}
    </div>

    <div class="la-quote">
      <p>"{s['tagline']}"</p>
    </div>

    <div class="la-sec">
      <div class="la-sec-hd">What I Cover</div>
      <div class="la-inv">
        {"".join(f'<div class="la-inv-card"><div class="la-inv-icon">{[ico_trend,ico_home,ico_pie,ico_dollar,ico_shield,ico_cal][i%6]}</div><div><div class="la-inv-head">{vp[0]}</div><div class="la-inv-body">{vp[1]}</div></div></div>' for i,vp in enumerate(s.get("leaf_vp",[("Dividend Investing","High-quality companies with consistent payout histories."),("REITs","Real estate investment trusts for income without direct property management."),("Index Funds","The low-cost, tax-efficient core that outperforms most active strategies."),("Digital Income","Products that generate recurring revenue once built and marketed."),("Fixed Income","Capital preservation and portfolio stability for when equities fall."),("Tax-Advantaged Accounts","Strategic use of registered accounts - the part most content gets wrong.")])))}
      </div>
    </div>

    <div class="la-sec">
      <div class="la-sec-hd">How I Approach {s['category']}</div>
      <div class="la-steps">
        {"".join(f'<div class="la-step"><div class="la-step-dot">{i+1}</div><div><div class="la-step-head">{st[0]}</div><div class="la-step-body">{st[1]}</div></div></div>' for i,st in enumerate(s.get("leaf_approach",[("Start with what the evidence shows","Before applying any strategy, understand what the research actually supports - not what popular sources claim."),("Layer complexity deliberately","Add one new layer at a time. Understand each piece before moving to the next."),("Run the realistic numbers","Most projections skip the hard parts: time, cost, and real-world friction. Do the honest math first."),("Structure beats hustle","How you organize your approach matters as much as what you do. Systems compound over time."),("Accept the realistic timeline","Meaningful results take time. Those who succeed are the ones who stopped looking for shortcuts.")])))}
      </div>
    </div>

    <div class="la-sec">
      <div class="la-sec-hd">About {s['name']}</div>
      <p class="la-p">{s['hero_sub']}</p>
      <p class="la-p">{s['footer_desc']}</p>
    </div>

    <div class="la-sec">
      <div class="la-sec-hd">Contributors</div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px">
        {_contributors_html(s,'var(--bg2)','var(--brd)','var(--txt)','var(--mut)','var(--pri)')}
      </div>
    </div>

    <div class="la-sec">
      <div class="la-sec-hd">Reader Comments</div>
      <div style="background:var(--bg2);border:1px solid var(--brd);border-radius:10px;padding:4px 20px">
        {_comments_html(s,'var(--bg2)','var(--brd)','var(--txt)','var(--mut)','var(--pri)')}
      </div>
    </div>

  </div>

  <aside class="la-side">

    <div class="la-nl">
      <h3>{s['nl_head']}</h3>
      <p>{s['nl_sub']}</p>
      <form id="la-nl-form" onsubmit="nlSub(event)">
        <input type="email" class="la-nl-in" placeholder="your@email.com" required>
        <button type="submit" class="la-nl-btn">Join the letter</button>
      </form>
    </div>

    <div class="la-card">
      <div class="la-card-lbl">Credentials</div>
      <p style="font-size:13px;color:var(--mut);line-height:1.8;margin-bottom:8px">{s['author_title']}</p>
      <p style="font-size:13px;color:var(--mut);line-height:1.8">No product affiliations. No sponsored recommendations. No incentive to tell you anything other than what the math actually shows.</p>
    </div>

    <div class="la-card">
      <div class="la-card-lbl">Topics Covered</div>
      <ul style="list-style:none;display:flex;flex-direction:column;gap:8px">
        <li style="font-size:13px;color:var(--mut);display:flex;align-items:center;gap:8px"><span style="color:var(--pri);font-weight:700">→</span> Dividend Investing</li>
        <li style="font-size:13px;color:var(--mut);display:flex;align-items:center;gap:8px"><span style="color:var(--pri);font-weight:700">→</span> REIT Analysis</li>
        <li style="font-size:13px;color:var(--mut);display:flex;align-items:center;gap:8px"><span style="color:var(--pri);font-weight:700">→</span> Index Fund Strategy</li>
        <li style="font-size:13px;color:var(--mut);display:flex;align-items:center;gap:8px"><span style="color:var(--pri);font-weight:700">→</span> Tax Optimization</li>
        <li style="font-size:13px;color:var(--mut);display:flex;align-items:center;gap:8px"><span style="color:var(--pri);font-weight:700">→</span> Early Retirement Math</li>
        <li style="font-size:13px;color:var(--mut);display:flex;align-items:center;gap:8px"><span style="color:var(--pri);font-weight:700">→</span> Income Portfolio Design</li>
      </ul>
    </div>

    <div class="la-card" id="la-recent-card">
      <div class="la-card-lbl">Recent Articles</div>
      <div id="la-recent-list" style="display:flex;flex-direction:column;gap:10px"></div>
    </div>

  </aside>
</div>

<div class="lfb">
  <span class="lfb-copy">© {s['name']}</span>
  <div class="lfb-links">
    <a href="./">Home</a><a href="about.html">About</a><a href="privacy.html">Privacy Policy</a><a href="terms.html">Terms</a><a href="sms.html">SMS Policy</a><a href="meta-policy.html">Meta Policy</a>
  </div>
</div>

<script>
function nlSub(e){{e.preventDefault();document.getElementById('la-nl-form').innerHTML='<div style="color:#fff;font-weight:600;padding:6px 0">Welcome to the letter.</div>';}}
async function loadRecent(){{
  try{{
    const r=await fetch('./articles.json');if(!r.ok)return;
    const posts=await r.json();
    const el=document.getElementById('la-recent-list');
    if(el)el.innerHTML=posts.slice(0,4).map(p=>`<a href="./${{p.slug||'#'}}/" style="text-decoration:none;display:block;border-bottom:1px solid var(--brd);padding-bottom:8px"><div style="font-family:'Lora',Georgia,serif;font-size:13px;font-weight:600;color:var(--txt);line-height:1.4;margin-bottom:3px">${{p.title}}</div><div style="font-size:10px;color:var(--mut)">${{p.date_iso||''}}</div></a>`).join('');
  }}catch(e){{}}
}}
loadRecent();
{pxjs}
</script>
</body></html>"""


# ── TEMPLATE: FORGE (industrial/specialty) ────────────────────────────────────
def forge_index(s):
    cv = css_vars(s)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{s['name']} - {s['tagline']}</title>
<meta name="description" content="{s['hero_sub']}">
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
:root{{{cv}}}
body{{font-family:var(--fb);background:var(--bg);color:var(--txt);font-size:15px;line-height:1.7}}
a{{color:var(--pri);text-decoration:none}}a:hover{{opacity:.85}}
[data-region=nav]{{background:var(--bg2);border-bottom:3px solid var(--pri);padding:16px 44px;display:flex;align-items:center;justify-content:space-between;position:sticky;top:0;z-index:99}}
.fg-mark{{font-size:20px;font-weight:900;color:var(--txt);letter-spacing:-0.5px;text-decoration:none;text-transform:uppercase}}
.fg-mark span{{color:var(--pri)}}
.fg-links{{display:flex;gap:28px}}.fg-links a{{font-size:13px;color:var(--mut);font-weight:600;text-transform:uppercase;letter-spacing:.5px;transition:color .2s}}.fg-links a:hover{{color:var(--txt)}}
[data-region=header]{{padding:72px 44px 56px;background:var(--bg2);border-bottom:1px solid var(--brd);position:relative;overflow:hidden}}
[data-region=header]::before{{content:'';position:absolute;left:0;top:0;width:4px;height:100%;background:var(--pri)}}
.fg-eyebrow{{font-size:11px;font-weight:800;color:var(--pri);text-transform:uppercase;letter-spacing:4px;margin-bottom:18px}}
[data-region=header] h1{{font-size:clamp(26px,3.5vw,48px);font-weight:900;line-height:1.1;letter-spacing:-0.5px;max-width:660px;margin-bottom:16px}}
[data-region=header] p{{font-size:15px;color:var(--mut);max-width:540px;line-height:1.85}}
[data-region=articles]{{padding:56px 44px;max-width:1160px;margin:0 auto}}
.fg-section-title{{font-size:11px;font-weight:800;text-transform:uppercase;letter-spacing:3px;color:var(--pri);margin-bottom:24px;display:flex;align-items:center;gap:12px}}
.fg-section-title::after{{content:'';flex:1;height:1px;background:var(--brd)}}
.fg-tiles{{display:grid;grid-template-columns:repeat(auto-fill,minmax(290px,1fr));gap:18px}}
.fg-tile{{background:var(--bg2);border-left:3px solid var(--pri);padding:22px 20px;display:flex;flex-direction:column;gap:8px;transition:border-color .2s}}
.fg-tile:hover{{border-color:var(--pri2)}}
.fg-tile-tag{{font-size:10px;font-weight:800;color:var(--pri);text-transform:uppercase;letter-spacing:2px}}
.fg-tile h3{{font-size:16px;font-weight:700;line-height:1.35;color:var(--txt)}}
.fg-tile p{{font-size:13px;color:var(--mut);line-height:1.75;flex:1}}
.fg-tile-foot{{display:flex;justify-content:space-between;align-items:center;margin-top:4px}}
.fg-tile-date{{font-size:11px;color:var(--mut)}}
.fg-tile-read{{font-size:12px;font-weight:700;color:var(--pri)}}
[data-region=subscribe]{{background:var(--sur);border-top:1px solid var(--brd);border-bottom:1px solid var(--brd);padding:64px 44px}}
.fg-sub-inner{{max-width:600px}}
[data-region=subscribe] h2{{font-size:clamp(20px,2.5vw,32px);font-weight:900;text-transform:uppercase;letter-spacing:-0.5px;margin-bottom:8px}}
[data-region=subscribe] p{{color:var(--mut);font-size:14px;margin-bottom:24px;line-height:1.8}}
.fg-sub-form{{display:flex;gap:10px;max-width:480px}}
.fg-sub-input{{flex:1;background:var(--bg);border:1px solid var(--brd);border-radius:4px;padding:12px 16px;color:var(--txt);font-size:14px;outline:none;transition:border-color .2s}}
.fg-sub-input:focus{{border-color:var(--pri)}}.fg-sub-input::placeholder{{color:var(--mut)}}
.fg-sub-btn{{background:var(--pri);color:#000;border:none;border-radius:4px;padding:12px 22px;font-size:14px;font-weight:800;cursor:pointer;text-transform:uppercase;letter-spacing:.5px;transition:background .2s;white-space:nowrap}}
.fg-sub-btn:hover{{background:var(--pri2)}}.fg-sub-ok{{color:var(--pri);font-weight:700;font-size:14px;padding:8px 0}}
[data-region=footer]{{padding:22px 44px;border-top:1px solid var(--brd);display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px}}
.fg-foot-copy{{font-size:12px;color:var(--mut)}}
.fg-foot-nav{{display:flex;gap:20px}}.fg-foot-nav a{{font-size:12px;color:var(--mut)}}
@media(max-width:700px){{[data-region=nav]{{padding:12px 16px}}[data-region=header]{{padding:48px 16px 36px}}[data-region=articles]{{padding:36px 16px}}[data-region=subscribe]{{padding:48px 16px}}.fg-sub-form{{flex-direction:column}}[data-region=footer]{{padding:20px 16px;flex-direction:column;text-align:center}}}}
</style>
</head>
<body>

<!-- nav -->
<div data-region="nav">
  <a href="./" class="fg-mark">{s['name'].split()[0]}<span> {' '.join(s['name'].split()[1:])}</span></a>
  <div class="fg-links"><a href="./">Home</a><a href="about.html">About</a></div>
</div>

<!-- hero -->
<div data-region="header">
  <div class="fg-eyebrow">{s['category']}</div>
  <h1>{s['tagline']}</h1>
  <p>{s['hero_sub']}</p>
</div>

<!-- pexels-banner -->
{_pexels_banner('210px')}

<!-- about section -->
{_about_block(s, s['surface'], s['brd'], s['text'], s['muted'], s['primary'])}

<!-- articles -->
<div data-region="articles">
  <div class="fg-section-title">Latest Articles</div>
  <div class="fg-tiles" id="fg-tiles"></div>
</div>

<!-- newsletter -->
<div data-region="subscribe">
  <div class="fg-sub-inner">
    <h2>{s['nl_head']}</h2>
    <p>{s['nl_sub']}</p>
    <form id="fg-nl" onsubmit="nlSub(event)">
      <div class="fg-sub-form">
        <input type="email" class="fg-sub-input" placeholder="your@email.com" required>
        <button type="submit" class="fg-sub-btn">Subscribe</button>
      </div>
    </form>
  </div>
</div>

<!-- footer -->
<div data-region="footer">
  <span class="fg-foot-copy">© {s['name']} - {s['footer_desc']}</span>
  <div class="fg-foot-nav"><a href="./">Home</a><a href="about.html">About</a><a href="privacy.html">Privacy Policy</a><a href="terms.html">Terms</a><a href="sms.html">SMS Policy</a><a href="meta-policy.html">Meta Policy</a></div>
</div>

<script>
/* load articles tiles */
async function loadPosts(){{
  const el=document.getElementById('fg-tiles');
  try{{
    const r=await fetch('./articles.json');if(!r.ok)throw 0;
    const posts=await r.json();if(!posts.length)throw 0;
    el.innerHTML=posts.slice(0,9).map(p=>`<div class="fg-tile" style="padding:0;overflow:hidden;">
      ${{p.image?`<a href="./${{p.slug||'#'}}/"><img src="${{p.image}}" alt="${{p.title}}" style="width:100%;height:170px;object-fit:cover;display:block;"></a>`:''}}
      <div style="padding:20px 22px;">
        <div class="fg-tile-tag">{s['category']}</div>
        <h3>${{p.title}}</h3>
        <p>${{p.meta_description||''}}</p>
        <div class="fg-tile-foot"><span class="fg-tile-date">${{p.date_iso||''}}</span><a class="fg-tile-read" href="./${{p.slug||'#'}}/">Read →</a></div>
      </div>
    </div>`).join('');
  }}catch(e){{
    el.innerHTML='<div class="fg-tile"><div class="fg-tile-tag">Coming Soon</div><h3>Articles publishing shortly</h3><p>Check back soon.</p></div>';
  }}
}}
function nlSub(e){{e.preventDefault();document.getElementById('fg-nl').innerHTML='<div class="fg-sub-ok">✓ You\'re on the list.</div>';}}
loadPosts();
{_pexels_js(s)}
</script>
</body></html>"""


def forge_about(s):
    cv = css_vars(s)
    ini = ''.join(w[0] for w in s['author'].split() if w)
    story = _story_html(s, 'fa-p')
    banner = _pexels_banner('230px')
    pxjs   = _pexels_js(s)
    nm_parts = s['name'].split()
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>About {s['author']} - {s['name']}</title>
<meta name="description" content="{s['footer_desc']}">
<style>
/* === reset === */
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
:root{{{cv}}}
body{{font-family:var(--fb);background:var(--bg);color:var(--txt);font-size:15px;line-height:1.7}}
a{{color:var(--pri);text-decoration:none}}a:hover{{opacity:.85}}
/* === nav === */
[data-region=nav]{{background:var(--bg2);border-bottom:3px solid var(--pri);padding:16px 44px;display:flex;align-items:center;justify-content:space-between;position:sticky;top:0;z-index:99}}
.fg-mark{{font-size:20px;font-weight:900;color:var(--txt);text-decoration:none;text-transform:uppercase}}
.fg-mark span{{color:var(--pri)}}.fg-links{{display:flex;gap:28px}}.fg-links a{{font-size:13px;color:var(--mut);font-weight:600;text-transform:uppercase;letter-spacing:.5px;transition:color .2s}}.fg-links a:hover{{color:var(--txt)}}
/* === author top bar === */
.fa-top{{background:var(--bg2);border-bottom:1px solid var(--brd);padding:52px 44px;display:flex;align-items:center;gap:28px}}
.fa-top::before{{content:'';display:block;width:4px;height:72px;background:var(--pri);flex-shrink:0}}
.fa-avi{{width:72px;height:72px;background:var(--pri);display:flex;align-items:center;justify-content:center;font-size:24px;font-weight:900;color:#000;flex-shrink:0}}
.fa-top-name{{font-size:26px;font-weight:900;text-transform:uppercase;letter-spacing:-0.5px;margin-bottom:4px}}
.fa-top-title{{font-size:12px;color:var(--pri);font-weight:700;text-transform:uppercase;letter-spacing:1.5px}}
/* === body === */
.fa-body{{max-width:760px;margin:0 auto;padding:52px 44px}}
.fa-block{{margin-bottom:40px}}
.fa-block-label{{font-size:10px;font-weight:800;text-transform:uppercase;letter-spacing:3px;color:var(--pri);margin-bottom:14px;display:flex;align-items:center;gap:12px}}
.fa-block-label::after{{content:'';flex:1;height:1px;background:var(--brd)}}
.fa-p{{color:var(--mut);line-height:1.85;margin-bottom:14px}}
/* === checklist credentials === */
.fa-credentials{{background:var(--sur);border-left:3px solid var(--pri);padding:20px 22px;margin-bottom:40px}}
.fa-cred-label{{font-size:10px;font-weight:800;text-transform:uppercase;letter-spacing:3px;color:var(--pri);margin-bottom:12px}}
.fa-cred-item{{display:flex;align-items:flex-start;gap:10px;margin-bottom:8px;color:var(--txt);font-size:13px}}
.fa-cred-item::before{{content:'--';color:var(--pri);font-weight:700;flex-shrink:0}}
/* === newsletter === */
.fg-nl-box{{background:var(--sur);border-left:3px solid var(--pri);padding:24px;margin-top:8px}}
.fg-nl-box h3{{font-size:15px;font-weight:900;text-transform:uppercase;margin-bottom:8px}}
.fg-nl-box p{{color:var(--mut);font-size:13px;margin-bottom:16px}}
.fg-sub-form2{{display:flex;gap:10px;max-width:420px}}
.fg-sub-input{{flex:1;background:var(--bg);border:1px solid var(--brd);border-radius:4px;padding:10px 14px;color:var(--txt);font-size:13px;outline:none;transition:border-color .2s}}
.fg-sub-input:focus{{border-color:var(--pri)}}.fg-sub-input::placeholder{{color:var(--mut)}}
.fg-sub-btn{{background:var(--pri);color:#000;border:none;border-radius:4px;padding:10px 18px;font-size:13px;font-weight:800;cursor:pointer;text-transform:uppercase;white-space:nowrap}}
.fg-sub-ok{{color:var(--pri);font-weight:700;font-size:13px;padding:6px 0}}
/* === footer === */
[data-region=footer]{{padding:22px 44px;border-top:1px solid var(--brd);display:flex;justify-content:space-between;flex-wrap:wrap;gap:10px;margin-top:20px}}
.fg-foot-copy,.fg-foot-nav a{{font-size:12px;color:var(--mut)}}.fg-foot-nav{{display:flex;gap:20px}}
@media(max-width:600px){{[data-region=nav]{{padding:12px 16px}}.fa-top{{padding:36px 16px;flex-direction:column;gap:14px}}.fa-top::before{{display:none}}.fa-body{{padding:36px 16px}}.fg-sub-form2{{flex-direction:column}}[data-region=footer]{{padding:20px 16px}}}}
</style>
</head>
<body>

<!-- nav -->
<div data-region="nav">
  <a href="./" class="fg-mark">{nm_parts[0]}<span> {' '.join(nm_parts[1:])}</span></a>
  <div class="fg-links"><a href="./">Home</a><a href="about.html">About</a></div>
</div>

<!-- author-top -->
<div class="fa-top">
  <div class="fa-avi">{ini}</div>
  <div>
    <div class="fa-top-name">{s['author']}</div>
    <div class="fa-top-title">{s['author_title']}</div>
  </div>
</div>

<!-- pexels-banner -->
{banner}

<!-- main-content -->
<div class="fa-body">

  <!-- section: background story -->
  <div class="fa-block">
    <div class="fa-block-label">Background</div>
    {story}
  </div>

  <!-- section: credentials -->
  <div class="fa-credentials">
    <div class="fa-cred-label">Credentials</div>
    <div class="fa-cred-item">{s['author_title']}</div>
    <div class="fa-cred-item">Covering the {s['category']} space</div>
    <div class="fa-cred-item">{s['name']} - independent publication</div>
  </div>

  <!-- section: this site -->
  <div class="fa-block">
    <div class="fa-block-label">This Site</div>
    <p class="fa-p">{s['hero_sub']}</p>
    <p class="fa-p">{s['footer_desc']}</p>
  </div>

  <!-- section: newsletter -->
  <div class="fg-nl-box">
    <h3>{s['nl_head']}</h3>
    <p>{s['nl_sub']}</p>
    <form id="abt-nl" onsubmit="nlSub(event)">
      <div class="fg-sub-form2">
        <input type="email" class="fg-sub-input" placeholder="your@email.com" required>
        <button type="submit" class="fg-sub-btn">Subscribe</button>
      </div>
    </form>
  </div>

</div>

<!-- section: contributors -->
<div style="max-width:900px;margin:0 auto;padding:40px 44px 0">
  <div style="font-size:11px;font-weight:900;text-transform:uppercase;letter-spacing:2px;color:var(--mut);margin-bottom:14px">-- CONTRIBUTORS</div>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:40px">
    {_contributors_html(s,'var(--sur)','var(--brd)','var(--txt)','var(--mut)','var(--pri)')}
  </div>
</div>

<!-- section: comments -->
<div style="max-width:900px;margin:0 auto;padding:0 44px 48px">
  <div style="font-size:11px;font-weight:900;text-transform:uppercase;letter-spacing:2px;color:var(--mut);margin-bottom:14px">-- READER COMMENTS</div>
  <div style="background:var(--sur);border-left:4px solid var(--pri);padding:4px 20px">
    {_comments_html(s,'var(--sur)','var(--brd)','var(--txt)','var(--mut)','var(--pri)')}
  </div>
</div>

<!-- footer -->
<div data-region="footer">
  <span class="fg-foot-copy">© {s['name']}</span>
  <div class="fg-foot-nav"><a href="./">Home</a><a href="about.html">About</a><a href="privacy.html">Privacy Policy</a><a href="terms.html">Terms</a><a href="sms.html">SMS Policy</a><a href="meta-policy.html">Meta Policy</a></div>
</div>

<script>
function nlSub(e){{e.preventDefault();e.target.innerHTML='<div class="fg-sub-ok">✓ Subscribed.</div>';}}
{pxjs}
</script>
</body></html>"""


# ── Legal page shared layout ───────────────────────────────────────────────────
def _legal_page(s, page_title, page_slug, body_html):
    """Wrap legal content in the site's homepage shell (header + footer + chrome).
    Content styling is self-contained with literal site colors so it never depends
    on or disturbs the homepage CSS variables."""
    ink = _ink_for(s)
    css = f""".lg-wrap{{max-width:820px;margin:0 auto;padding:52px 24px 84px}}
.lg-title{{font-family:{s['font_head']};font-size:clamp(26px,4vw,34px);font-weight:800;margin:0 0 8px;line-height:1.15;color:{ink}}}
.lg-meta{{font-size:12px;color:{s['muted']};margin-bottom:36px;padding-bottom:20px;border-bottom:1px solid {s['brd']}}}
.lg-h2{{font-family:{s['font_head']};font-size:18px;font-weight:700;margin:30px 0 10px;color:{s['primary']}}}
.lg-p{{color:{s['muted']};margin-bottom:13px;line-height:1.85;font-size:15px}}
.lg-p b,.lg-p strong{{color:{ink}}}
.lg-p a{{color:{s['primary']}}}
.lg-ul{{color:{s['muted']};margin:0 0 13px 22px;line-height:1.9;font-size:15px}}
.lg-ul li{{margin-bottom:4px}}
.lg-box{{background:{s['bg2']};border:1px solid {s['brd']};border-radius:6px;padding:16px 20px;margin:16px 0 20px}}
@media(max-width:640px){{.lg-wrap{{padding-left:16px;padding-right:16px}}}}"""
    body = f"""<main class="lg-wrap">
  <h1 class="lg-title">{page_title}</h1>
  <div class="lg-meta">Applies to: <strong>{s['name']}</strong> | Last updated: May 1, 2025</div>
  {body_html}
</main>"""
    return layout_shell.wrap_page(
        s['id'], title=f"{page_title} - {s['name']}",
        description=f"{page_title} for {s['name']}.",
        body_html=body, extra_css=css, depth=0,
    )


def _niche_disclaimer(s):
    cat = s['category']
    financial = {"Crypto & Trading","Trading Technology","Passive Income & Investing","Real Estate Investing","Ecommerce Strategy","Online Business","Insurance"}
    medical = {"Sports Performance","Fitness & Training","Supplement Science","Newborn & Baby Care","Dating & Relationships","Makeup & Beauty"}
    legal = {"Construction & Renovation","Real Estate Investing"}
    if cat in financial:
        return f"""<div class="lg-h2">Financial Information Disclaimer</div>
<div class="lg-box"><p class="lg-p"><strong>Nothing on {s['name']} is financial, investment, or professional advice.</strong> All content is published for educational and informational purposes only. {s['author']} is not a licensed financial advisor, broker, or investment professional. The information published here reflects personal research and opinion and should not be relied upon to make financial decisions. Past performance discussed does not guarantee future results. Investing and trading involve risk of loss. Always consult a licensed financial professional before making investment decisions.</p></div>"""
    elif cat in medical:
        return f"""<div class="lg-h2">Health and Wellness Disclaimer</div>
<div class="lg-box"><p class="lg-p"><strong>Content on {s['name']} is for educational purposes only and does not constitute medical advice.</strong> Nothing published here should replace the advice of a qualified healthcare provider, licensed physician, registered dietitian, or certified health professional. Individual health conditions vary significantly. Before beginning any new exercise program, supplement regimen, or making changes to your health routine, consult with a qualified medical professional. {s['author']} does not diagnose, treat, or prescribe.</p></div>"""
    else:
        return f"""<div class="lg-h2">Informational Content Disclaimer</div>
<div class="lg-box"><p class="lg-p"><strong>Content on {s['name']} is published for informational and educational purposes only.</strong> While {s['author']} takes care to ensure accuracy, the information provided does not constitute professional advice in any regulated field. For decisions with significant financial, legal, health, or safety implications, please consult a qualified professional with knowledge of your specific circumstances.</p></div>"""


def gen_privacy(s):
    niche_data = {
        "Crypto & Trading": "trading analysis consumption patterns and portfolio interest indicators",
        "Trading Technology": "software tool preferences and development workflow signals",
        "EV & Automotive": "vehicle ownership status and automotive research interests",
        "AI Marketing": "marketing technology stack preferences and campaign management behavior",
        "Online Business": "business model preferences and entrepreneurship stage indicators",
        "Sports Performance": "athletic training level, sport category, and performance goal signals",
        "Dating & Relationships": "relationship status indicators and content topic preferences",
        "Fitness & Training": "fitness goal categories and training frequency signals",
        "Supplement Science": "nutrition protocol interests and fitness category signals",
        "Ecommerce Strategy": "platform preferences and business scale indicators",
        "Insurance": "insurance category interests and coverage research patterns",
        "Real Estate Investing": "investment strategy preferences and property market interests",
        "Newborn & Baby Care": "parenting stage and child age range for content personalization",
        "Passive Income & Investing": "investment vehicle interests and income strategy preferences",
        "Pet Care & Dog Breeds": "pet ownership type, breed category, and care question patterns",
        "Music Education": "instrument type, skill level, and practice frequency signals",
        "Home Design & Real Estate": "property type, renovation scope, and design style preferences",
        "Gifts & Lifestyle": "gift occasion type, budget range signals, and product interest categories",
        "Makeup & Beauty": "skin type indicators, skill level, and product category preferences",
        "Travel & Destinations": "destination type preferences, travel frequency, and trip planning stage",
        "Construction & Renovation": "project type, property ownership status, and budget range signals",
        "Event Planning": "event type, guest count range, and planning timeline indicators",
    }
    note = niche_data.get(s['category'], "content consumption patterns and topic interests")
    body = f"""<div class="lg-h2">1. Who We Are</div>
<p class="lg-p"><strong>{s['name']}</strong> is an independent content publication operated by {s['author']}, focused on the {s['category']} space. This policy covers all information collected through this website and our newsletter. We are committed to handling your data responsibly and transparently.</p>
<p class="lg-p">We do not sell personal information. We do not operate a data brokerage. We do not share your data with advertisers directly. Everything described below exists solely to operate this publication.</p>

<div class="lg-h2">2. Information We Collect</div>
<p class="lg-p"><strong>Information you provide:</strong> When you subscribe to our newsletter, you provide an email address. That address is stored in our email service provider (Brevo) and used only to send the newsletter you requested. We do not require names, phone numbers, or payment details to access content on this site.</p>
<p class="lg-p"><strong>Automatically collected information:</strong> Standard web server logs record IP addresses, browser type, operating system, referring URL, and pages visited. We analyze this data in aggregate to understand traffic - we do not use it to build profiles of individual visitors.</p>
<p class="lg-p"><strong>Third-party behavioral data:</strong> This site uses Google Analytics and Meta Pixel. These tools may collect {note} as behavioral signals to help us understand which content is most useful. See Section 5 for opt-out options.</p>

<div class="lg-h2">3. How We Use Your Information</div>
<p class="lg-p">We use the information we collect for the following purposes only:</p>
<ul class="lg-ul">
  <li>Delivering the newsletter you subscribed to, including occasional updates about new content</li>
  <li>Analyzing aggregate site traffic to improve the quality and relevance of content we publish</li>
  <li>Understanding reader interests to guide future publishing decisions within the {s['category']} topic area</li>
  <li>Measuring the performance of any advertising we run on platforms like Facebook or Instagram</li>
</ul>
<p class="lg-p">We do not use your information for automated profiling, targeted advertising sold to third parties, or any commercial purpose beyond operating this publication. Every newsletter email includes a one-click unsubscribe link.</p>

<div class="lg-h2">4. Third-Party Service Providers</div>
<p class="lg-p">We share data only with the service providers necessary to operate this site:</p>
<ul class="lg-ul">
  <li><strong>Brevo</strong> - email delivery. Your email address is stored here to send the newsletter. Brevo's privacy policy is available at brevo.com/legal/privacypolicy.</li>
  <li><strong>GitHub Pages</strong> - website hosting. No personal data is stored by the host beyond standard server logs.</li>
  <li><strong>Google Analytics</strong> - aggregate traffic analysis. IP addresses are anonymized before processing. Opt out at tools.google.com/dlpage/gaoptout.</li>
  <li><strong>Meta Pixel</strong> - advertising measurement. See our Meta Policy page for full details. Opt out at facebook.com/ads/preferences.</li>
</ul>

<div class="lg-h2">5. Cookies and Tracking</div>
<p class="lg-p">This site uses the following types of cookies:</p>
<ul class="lg-ul">
  <li><strong>Analytics cookies</strong> (Google Analytics) - track page views and session patterns in aggregate</li>
  <li><strong>Advertising measurement cookies</strong> (Meta Pixel) - measure ad effectiveness</li>
  <li>No first-party session cookies or tracking cookies are set by this site directly</li>
</ul>
<p class="lg-p">You can block or delete cookies through your browser settings. Most modern browsers allow you to control cookie behavior at a granular level. Blocking analytics cookies does not affect your ability to read content on this site.</p>

<div class="lg-h2">6. Your Rights</div>
<p class="lg-p">Depending on your location, you may have rights including: the right to access personal data we hold about you; the right to correct inaccurate information; the right to request deletion of your data; the right to object to certain processing; and the right to data portability.</p>
<p class="lg-p"><strong>California residents</strong> have additional rights under the CCPA, including the right to know what personal information is collected and to opt out of its sale. We do not sell personal information.</p>
<p class="lg-p"><strong>EEA and UK residents</strong> have rights under GDPR, including the right to lodge a complaint with a supervisory authority.</p>
<p class="lg-p">To exercise any right, contact us using the information in Section 9. We respond within 30 days.</p>

<div class="lg-h2">7. Data Retention</div>
<p class="lg-p">Newsletter subscriber email addresses are retained for as long as you remain subscribed. Upon unsubscribing, your email is removed from the active list and deleted from Brevo within 30 days. Server logs are retained for a maximum of 90 days. Anonymized aggregate analytics data may be retained indefinitely as it cannot be traced back to any individual.</p>

<div class="lg-h2">8. Data Security</div>
<p class="lg-p">We implement reasonable security measures to protect the limited personal data we collect. This includes using HTTPS on all pages, relying on reputable service providers with their own security programs, and limiting access to subscriber data to the site operator only. No method of transmission over the internet is 100% secure; we cannot guarantee absolute security.</p>

<div class="lg-h2">9. Children's Privacy</div>
<p class="lg-p">This site is not directed at children under 13. We do not knowingly collect personal information from children under 13. If you believe a child under 13 has subscribed to our newsletter, contact us immediately and we will delete that information without delay.</p>

<div class="lg-h2">10. Changes to This Policy</div>
<p class="lg-p">We may update this privacy policy periodically. When we do, we update the date at the top of this page. Continued use of this site after changes are posted constitutes acceptance of the revised policy. We encourage you to review this page periodically.</p>

<div class="lg-h2">11. Contact Us</div>
<p class="lg-p">For privacy questions, data requests, or concerns, contact <strong>{s['author']}</strong> at {s['name']}. We take all privacy concerns seriously and will respond within 30 days of receiving your request.</p>"""
    return _legal_page(s, "Privacy Policy", "privacy", body)


def gen_terms(s):
    disclaimer = _niche_disclaimer(s)
    body = f"""<div class="lg-h2">1. Acceptance of Terms</div>
<p class="lg-p">By accessing or using <strong>{s['name']}</strong> (this "Site"), you agree to be bound by these Terms and Conditions. If you do not agree to these terms, please do not use this site. These terms apply to all visitors, subscribers, and users of this site.</p>
<p class="lg-p">We reserve the right to update these terms at any time. Changes take effect when posted. Your continued use of the site after changes are posted constitutes your acceptance of the revised terms.</p>

<div class="lg-h2">2. Nature of Content</div>
<p class="lg-p"><strong>{s['name']}</strong> is an independent publication operated by {s['author']}. All articles, guides, newsletters, and other content published on this site represent the author's personal research, experience, and opinion. Content is published in the {s['category']} category and reflects ongoing analysis in this space.</p>
<p class="lg-p">Content is published for informational and educational purposes. We strive for accuracy and update content when information changes, but we make no warranty that all content is current, complete, or error-free at the time you read it.</p>

{disclaimer}

<div class="lg-h2">3. Intellectual Property</div>
<p class="lg-p">All content on this site - including articles, analysis, graphics, and the newsletter - is the intellectual property of {s['author']} and {s['name']} unless otherwise attributed. Content is protected by copyright law.</p>
<p class="lg-p">You may share links to individual articles. You may quote brief excerpts (under 150 words) with proper attribution and a link back to the original article. You may not republish full articles, scrape content for AI training, or repurpose content commercially without written permission.</p>

<div class="lg-h2">4. Newsletter Terms</div>
<p class="lg-p">By subscribing to the {s['nl_head']} newsletter, you agree to receive periodic emails from {s['name']}. We send newsletters on an irregular schedule, typically ranging from weekly to monthly depending on the volume of material worth publishing.</p>
<p class="lg-p">You can unsubscribe at any time using the link in every email. We do not send unsolicited commercial email. We do not rent or sell our subscriber list to third parties. Each email complies with the CAN-SPAM Act requirements.</p>

<div class="lg-h2">5. Affiliate Links and Sponsorships</div>
<p class="lg-p">This site may contain affiliate links. If you click a link and make a purchase, we may receive a commission at no additional cost to you. We disclose affiliate relationships at the top of any article that contains them. Our editorial opinions are not influenced by affiliate arrangements - we write about what we genuinely find valuable in the {s['category']} space.</p>
<p class="lg-p">We do not accept paid guest posts or sponsored content that is presented as independent editorial opinion. Any sponsored content is clearly labeled as such.</p>

<div class="lg-h2">6. User Conduct</div>
<p class="lg-p">When using this site, you agree not to:</p>
<ul class="lg-ul">
  <li>Attempt to gain unauthorized access to any part of the site</li>
  <li>Use automated tools to scrape or harvest content from this site</li>
  <li>Use content from this site to train AI models without written permission</li>
  <li>Submit false information when subscribing to the newsletter</li>
  <li>Engage in any activity that interferes with the site's operation</li>
</ul>

<div class="lg-h2">7. Third-Party Links</div>
<p class="lg-p">This site may link to third-party websites for reference or additional information. We are not responsible for the content, privacy practices, or accuracy of third-party sites. Linking to a site does not constitute an endorsement. You visit linked sites at your own risk.</p>

<div class="lg-h2">8. Limitation of Liability</div>
<p class="lg-p">To the maximum extent permitted by applicable law, {s['name']} and {s['author']} shall not be liable for any indirect, incidental, special, consequential, or punitive damages arising from your use of this site or reliance on any content published here. This includes but is not limited to financial losses, health outcomes, or business decisions made based on content found on this site.</p>
<p class="lg-p">Our total liability to you for any claim arising from use of this site shall not exceed the amount you paid us in the 12 months preceding the claim - which in most cases is zero, as this site is free to access.</p>

<div class="lg-h2">9. Governing Law</div>
<p class="lg-p">These terms are governed by applicable law. Any disputes arising from these terms or use of this site will be resolved through good-faith negotiation first. We prefer direct resolution to litigation.</p>

<div class="lg-h2">10. Contact</div>
<p class="lg-p">Questions about these terms can be directed to <strong>{s['author']}</strong> at {s['name']}. We respond to all inquiries within 10 business days.</p>"""
    return _legal_page(s, "Terms and Conditions", "terms", body)


def gen_sms(s):
    body = f"""<div class="lg-h2">Overview</div>
<p class="lg-p">This SMS Policy governs text message communications from <strong>{s['name']}</strong>, operated by {s['author']}. We are committed to compliance with the Telephone Consumer Protection Act (TCPA), the CAN-SPAM Act, and all applicable federal and state regulations governing text message marketing and communications.</p>
<p class="lg-p">We take opt-in consent seriously. We do not send unsolicited text messages. Every person who receives an SMS from {s['name']} has explicitly provided consent to do so.</p>

<div class="lg-h2">How We Collect SMS Consent</div>
<p class="lg-p">We collect consent to send SMS messages through the following channels only:</p>
<ul class="lg-ul">
  <li>Web forms on this site where you explicitly check a box or enter your phone number and agree to receive text messages</li>
  <li>Verbal confirmation during a direct consultation or onboarding call, followed by written confirmation</li>
  <li>Reply to a promotional message where the call-to-action explicitly states that replying constitutes consent to receive SMS updates</li>
</ul>
<p class="lg-p">We never add phone numbers to our SMS list without explicit opt-in consent. Subscribing to our email newsletter does not constitute consent to receive SMS messages. These are separate opt-in processes.</p>

<div class="lg-h2">Types of SMS Messages We Send</div>
<p class="lg-p">When you opt in to SMS communications from {s['name']}, you may receive:</p>
<ul class="lg-ul">
  <li>Alerts when new articles or guides are published in the {s['category']} space</li>
  <li>Newsletter delivery via SMS when you have chosen SMS as a delivery preference</li>
  <li>Occasional updates about significant developments relevant to our {s['category']} content</li>
  <li>One-time transactional messages confirming your opt-in or opt-out</li>
</ul>
<p class="lg-p"><strong>Message frequency:</strong> We send SMS messages infrequently. Typical frequency is 2 to 6 messages per month, depending on content publishing schedule. We do not send daily promotional blasts.</p>
<p class="lg-p"><strong>Message and data rates may apply.</strong> Standard carrier rates apply for all text messages you receive from us. {s['name']} does not charge for SMS messages on our end, but your mobile carrier may charge for receiving text messages depending on your plan.</p>

<div class="lg-h2">How to Opt Out</div>
<p class="lg-p">You can opt out of SMS communications from {s['name']} at any time using any of the following methods:</p>
<ul class="lg-ul">
  <li><strong>Reply STOP</strong> to any text message you receive from us. You will receive one confirmation message and then no further SMS messages.</li>
  <li><strong>Reply UNSUBSCRIBE</strong> to any text message you receive from us. Same result as STOP.</li>
  <li><strong>Email us</strong> requesting removal from our SMS list. Include the phone number you wish to remove. We will confirm removal within 3 business days.</li>
</ul>
<p class="lg-p">Upon receiving a STOP request, we will add your number to our do-not-contact list immediately. You may continue to receive a single confirmation message after opting out. No further SMS messages will be sent after that confirmation.</p>
<p class="lg-p">Opting out of SMS does not affect your email newsletter subscription. These are managed separately.</p>

<div class="lg-h2">How to Get Help</div>
<p class="lg-p">For help with your SMS subscription, reply <strong>HELP</strong> to any text message you receive from us. You can also contact us directly at {s['name']}. We will respond to all help requests within 2 business days.</p>

<div class="lg-h2">Privacy of Your Phone Number</div>
<p class="lg-p">Your phone number is used only to send you the SMS messages you opted in to receive. We do not sell, rent, or share phone numbers with third parties for marketing purposes. Phone numbers are stored in our SMS service provider's system and are subject to their privacy and security practices. We have reviewed our SMS provider and selected them based on their compliance with TCPA and data security standards.</p>
<p class="lg-p">We retain your phone number on our SMS list for as long as you remain opted in. Upon opting out, your number is removed from our active list and added to our suppression list to ensure we do not contact you again. Numbers on the suppression list are retained to prevent accidental re-enrollment.</p>

<div class="lg-h2">Supported Carriers</div>
<p class="lg-p">SMS messaging from {s['name']} is compatible with all major US carriers including AT&T, Verizon, T-Mobile, Sprint, and regional carriers. We cannot guarantee message delivery on all carriers in all circumstances, particularly international carriers. If you are not receiving our SMS messages, check with your carrier to ensure short code or long code messages are not being blocked.</p>

<div class="lg-h2">Changes to This Policy</div>
<p class="lg-p">We may update this SMS policy from time to time to reflect changes in our practices or applicable law. When we make changes, we update the date on this page. If changes are material, we may notify active SMS subscribers by text message. Continued enrollment in our SMS program after changes are posted constitutes acceptance of the revised policy.</p>

<div class="lg-h2">Contact</div>
<p class="lg-p">For questions about this SMS Policy or to manage your SMS subscription, contact <strong>{s['author']}</strong> at {s['name']}. We are committed to transparent and compliant SMS communication.</p>"""
    return _legal_page(s, "SMS Compliance Policy", "sms", body)


def gen_meta_policy(s):
    body = f"""<div class="lg-h2">Overview</div>
<p class="lg-p"><strong>{s['name']}</strong>, operated by {s['author']}, uses Meta (Facebook) advertising tools to measure the performance of content and advertising campaigns. This page explains specifically how Meta's tools are deployed on this site, what data is collected, how it is used, and what your options are.</p>
<p class="lg-p">Meta's tools - primarily the Meta Pixel and the Conversions API - are advertising measurement technologies operated by Meta Platforms, Inc. (Menlo Park, California). This page supplements our Privacy Policy and provides Meta-specific transparency required by Meta's advertising policies and applicable privacy law.</p>

<div class="lg-h2">What the Meta Pixel Does</div>
<p class="lg-p">The Meta Pixel is a small piece of JavaScript code installed on this website. When you visit a page on {s['name']}, the Pixel fires and sends certain information to Meta. Specifically, the Pixel collects:</p>
<ul class="lg-ul">
  <li>The URL of the page you visited</li>
  <li>Your IP address (which Meta may use to match you to a Facebook or Instagram account)</li>
  <li>Browser type and operating system</li>
  <li>A unique browser identifier stored in a cookie</li>
  <li>Standard event data - for example, whether you viewed a specific article, scrolled to the bottom of a page, or clicked a newsletter signup button</li>
</ul>
<p class="lg-p">We use this data to understand which content drives engagement, to measure the effectiveness of any paid advertising we run on Facebook or Instagram, and to build Custom Audiences of people who have shown interest in {s['category']} content so we can reach similar audiences.</p>

<div class="lg-h2">Custom Audiences</div>
<p class="lg-p">Based on Meta Pixel data, we may create Custom Audiences in our Meta Ads account. These audiences allow us to show advertising on Facebook and Instagram to people who have previously visited this site. For example, we might show newsletter sign-up ads to people who read multiple articles but did not subscribe.</p>
<p class="lg-p">We may also create Lookalike Audiences - groups of people on Meta's platforms who share characteristics with our existing audience. Lookalike Audiences are built by Meta using its own matching algorithms; we do not have access to the individual data Meta uses to construct them.</p>
<p class="lg-p">We do not use Custom Audiences created from {s['name']} data to run advertising on behalf of third parties. These audiences are used exclusively for {s['name']} promotional purposes.</p>

<div class="lg-h2">Data Sharing with Meta</div>
<p class="lg-p">Through the Meta Pixel, the following categories of data may be shared with Meta Platforms, Inc.:</p>
<ul class="lg-ul">
  <li>Browsing behavior on this site (pages viewed, time on site, interactions)</li>
  <li>IP addresses (used by Meta for account matching)</li>
  <li>Cookie identifiers that may link your visit to a Meta account</li>
  <li>Email address hashed (if you sign up for our newsletter and we activate the advanced matching feature)</li>
</ul>
<p class="lg-p">Meta uses this data in accordance with its own Data Policy, available at facebook.com/privacy/policy. Meta may combine data received from our Pixel with data from other sources to build advertising profiles. We do not control how Meta processes data received from our Pixel beyond what is configured in our Meta Ads Manager settings.</p>

<div class="lg-h2">Meta's Use of Your Data</div>
<p class="lg-p">Meta may use data collected through our Pixel for its own purposes, including improving ad targeting across its platforms, building advertising models, and personalizing content shown to you on Facebook and Instagram. Meta's use of this data is governed by Meta's Data Policy, not by this policy.</p>
<p class="lg-p">If you have a Facebook or Instagram account, Meta may associate your visit to {s['name']} with your account based on your IP address, browser cookies, or login state.</p>

<div class="lg-h2">Your Options and Opt-Out</div>
<p class="lg-p">You have several options for controlling the Meta Pixel's collection of data from your visits to this site:</p>
<ul class="lg-ul">
  <li><strong>Facebook Ad Preferences:</strong> Visit facebook.com/ads/preferences to review and adjust your ad preferences, including interest-based advertising settings.</li>
  <li><strong>Off-Facebook Activity:</strong> Visit facebook.com/off-facebook-activity to review and disconnect activity that businesses and organizations have shared with Meta about you, including visits to this site.</li>
  <li><strong>Browser settings:</strong> Blocking third-party cookies in your browser will prevent the Meta Pixel from setting cookies on your device. Note that this may not prevent all Pixel data collection.</li>
  <li><strong>Browser extensions:</strong> Ad blockers and privacy-focused browser extensions (such as uBlock Origin or Privacy Badger) typically block the Meta Pixel.</li>
  <li><strong>Do Not Track:</strong> This site honors browser Do Not Track signals to the extent technically possible, but Meta's own processing of data is governed by their policies.</li>
</ul>

<div class="lg-h2">Data Retention</div>
<p class="lg-p">Custom Audiences created from {s['name']} Pixel data are retained in our Meta Ads account for as long as we operate advertising campaigns. We delete unused audiences periodically. Meta retains the underlying event data it collects through the Pixel according to its own data retention policies.</p>

<div class="lg-h2">Legal Basis for Processing</div>
<p class="lg-p">For visitors in the European Economic Area (EEA) or United Kingdom, our use of the Meta Pixel is based on our legitimate interest in measuring content performance and advertising effectiveness. You have the right to object to this processing. To exercise this right, use the opt-out options described above or contact us directly.</p>

<div class="lg-h2">Contact</div>
<p class="lg-p">For questions about our use of Meta advertising tools, contact <strong>{s['author']}</strong> at {s['name']}. For questions about Meta's own data practices, visit Meta's Help Center at facebook.com/help or contact Meta directly at facebook.com/privacy.</p>"""
    return _legal_page(s, "Meta / Facebook Data Policy", "meta-policy", body)


# ── 404 page ──────────────────────────────────────────────────────────────────
def gen_404(s):
    """404 page wrapped in the homepage shell. The Back link is resolved by a small
    script so it points to the site root regardless of the missing URL's depth."""
    ink = _ink_for(s)
    css = f""".e404{{max-width:560px;margin:0 auto;padding:88px 24px 96px;text-align:center}}
.e404-code{{font-family:{s['font_head']};font-size:96px;font-weight:900;color:{s['primary']};opacity:.28;line-height:1;margin-bottom:8px}}
.e404-title{{font-family:{s['font_head']};font-size:26px;font-weight:800;margin-bottom:12px;color:{ink}}}
.e404-sub{{font-size:15px;color:{s['muted']};line-height:1.75;margin-bottom:28px}}
.e404-back{{display:inline-block;background:{s['primary']};color:{s['bg']};border-radius:6px;padding:12px 28px;font-size:15px;font-weight:700;text-decoration:none;transition:opacity .2s}}
.e404-back:hover{{opacity:.85}}"""
    body = f"""<main class="e404">
  <div class="e404-code">404</div>
  <div class="e404-title">This page isn't here</div>
  <div class="e404-sub">The link may have changed or the article is still publishing. New articles appear on the homepage within 24 hours.</div>
  <a id="e404-back" class="e404-back" href="./">Back to {s['name']}</a>
</main>
<script>
(function(){{var p=location.pathname.split('/').filter(Boolean);
var root=p.length>1?'/'+p[0]+'/':'/';
var b=document.getElementById('e404-back');if(b)b.href=root;}})();
</script>"""
    return layout_shell.wrap_page(
        s['id'], title=f"Page Not Found - {s['name']}",
        body_html=body, extra_css=css, depth=0,
    )


def gen_about(s):
    """About page wrapped in the homepage shell. If a bespoke body fragment exists at
    about-bodies/<id>.html it is used; otherwise a unified fallback layout is built."""
    frag = BASE / "about-bodies" / f"{s['id']}.html"
    if frag.exists():
        return layout_shell.wrap_page(
            s['id'], title=f"About - {s['name']}",
            description=f"About {s['name']}: {s['footer_desc']}",
            body_html=frag.read_text(encoding="utf-8"), depth=0,
        )
    ini   = ''.join(w[0].upper() for w in s['author'].split()[:2])
    story = _story_html(s, css_class='ab-p')
    contributors = _site_contributors(s, 3)
    if contributors:
        team_cards = '\n      '.join(
            f"""<div class="ab-card">
        <div class="ab-card-av">{c['avatar']}</div>
        <div class="ab-card-name">{c['name']}</div>
        <div class="ab-card-role">{c['role']}</div>
        <div class="ab-card-bio">{c.get('bio','')}</div>
      </div>""" for c in contributors)
        contributors_block = f'''<div class="ab-h2">Who contributes</div>
  <p class="ab-p">Alongside {s['author']}, a small group of practitioners review and pressure-test what gets published here.</p>
  <div class="ab-grid">
      {team_cards}
  </div>'''
    else:
        contributors_block = ''
    team = ''  # legacy variable retained for template substitution compatibility

    # Use the actual page-body ink (parsed from the homepage shell) for headings/names
    # so they stay readable even when SITES['text'] is tuned for the nav (e.g. cream-on-dark)
    # while the page body is light (e.g. MindFrame's cream paper body).
    ink     = _ink_for(s)
    on_ink  = s.get('bg') or '#0b0b0b'  # text-on-primary buttons/avatars

    css = f""".ab{{max-width:840px;margin:0 auto;padding:56px 24px 88px}}
.ab-kicker{{font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:2.5px;color:{s['primary']};margin-bottom:14px}}
.ab-title{{font-family:{s['font_head']};font-size:clamp(28px,5vw,42px);font-weight:800;line-height:1.15;color:{ink};margin:0 0 16px}}
.ab-lead{{font-size:17px;line-height:1.7;color:{s['muted']};margin-bottom:40px}}
.ab-author{{display:flex;gap:16px;align-items:center;background:{s['bg2']};border:1px solid {s['brd']};border-radius:10px;padding:20px 22px;margin-bottom:32px}}
.ab-avatar{{width:56px;height:56px;border-radius:50%;background:{s['primary']};color:{on_ink};font-size:18px;font-weight:800;display:flex;align-items:center;justify-content:center;flex-shrink:0}}
.ab-name{{font-size:17px;font-weight:700;color:{ink}}}
.ab-role{{font-size:13px;color:{s['primary']};font-weight:600;margin-top:2px}}
.ab-h2{{font-family:{s['font_head']};font-size:20px;font-weight:700;color:{ink};margin:40px 0 14px}}
.ab-p{{font-size:15px;line-height:1.85;color:{s['muted']};margin-bottom:14px}}
.ab-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:16px;margin-top:14px}}
.ab-card{{background:{s['bg2']};border:1px solid {s['brd']};border-radius:10px;padding:18px}}
.ab-card-av{{width:38px;height:38px;border-radius:50%;background:{s['primary']};color:{on_ink};font-size:13px;font-weight:800;display:flex;align-items:center;justify-content:center;margin-bottom:10px}}
.ab-card-name{{font-size:14px;font-weight:700;color:{ink}}}
.ab-card-role{{font-size:11px;font-weight:600;color:{s['primary']};margin:2px 0 7px}}
.ab-card-bio{{font-size:12px;line-height:1.65;color:{s['muted']}}}
.ab-cta{{margin-top:44px;background:{s['bg2']};border:1px solid {s['brd']};border-radius:12px;padding:30px 26px;text-align:center}}
.ab-cta h3{{font-family:{s['font_head']};font-size:19px;font-weight:700;color:{ink};margin:0 0 8px}}
.ab-cta p{{font-size:14px;color:{s['muted']};margin:0 0 18px}}
.ab-cta a{{display:inline-block;background:{s['primary']};color:{on_ink};padding:11px 28px;border-radius:7px;font-size:14px;font-weight:700;text-decoration:none}}"""

    body = f"""<main class="ab">
  <div class="ab-kicker">About {s['name']}</div>
  <h1 class="ab-title">{s['tagline']}</h1>
  <p class="ab-lead">{s['hero_sub']}</p>
  <div class="ab-author">
    <div class="ab-avatar">{ini}</div>
    <div>
      <div class="ab-name">{s['author']}</div>
      <div class="ab-role">{s['author_title']}</div>
    </div>
  </div>
  <div class="ab-h2">Why this site exists</div>
  {story}
  {contributors_block}
  <div class="ab-cta">
    <h3>{s['nl_head']}</h3>
    <p>{s['nl_sub']}</p>
    <a href="./">Read the latest</a>
  </div>
</main>"""
    return layout_shell.wrap_page(
        s['id'], title=f"About - {s['name']}",
        description=f"About {s['name']}: {s['footer_desc']}",
        body_html=body, extra_css=css, depth=0,
    )


# ── All Articles index ───────────────────────────────────────────────────────
def _articles_categories(stem):
    """Return the category list for a site stem from categories.json. Falls back
    to an empty list when the site has no entry. Safe to call repeatedly."""
    try:
        path = BASE / "categories.json"
        if not path.exists():
            return []
        data = json.loads(path.read_text(encoding="utf-8"))
        entry = data.get(stem) or {}
        cats = entry.get("categories") or []
        return [str(c) for c in cats if c]
    except Exception:
        return []


def _articles_body_editorial(s):
    """Editorial luxury archive variant (opt-in via site config 'editorial_archive':true).
    Used by kanona-events; restrained dark editorial layout with a feature hero,
    2-col article cards in 4:5 portrait crop, italic-serif accents, no chip row
    or 'X published' badge. Premium feel matching a monograph index."""
    ink    = _ink_for(s)
    on_ink = s.get('bg') or '#000'
    accent = s.get('primary', '#c4a05d')
    bg     = s.get('bg', '#050407')
    bg2    = s.get('bg2', '#0a0810')
    surf   = s.get('surface', '#0e0b15')
    text   = s.get('text', '#e8e2d9')
    muted  = s.get('muted', 'rgba(232,226,217,.6)')
    border = s.get('brd', 'rgba(255,255,255,.06)')
    fhead  = s.get('font_head', "'Cormorant Garamond',Georgia,serif")
    fmono  = s.get('font_mono', "'JetBrains Mono',ui-monospace,monospace")
    fallback_img = ("https://images.unsplash.com/photo-1519671482749-fd09be7ccebf"
                    "?w=1400&q=85&auto=format&fit=crop")

    css = f""".jr{{max-width:1180px;margin:0 auto;padding:48px 28px 120px;color:{text}}}
.jr-head{{text-align:center;margin:0 auto 56px;max-width:760px}}
.jr-eyebrow{{font-family:{fmono};font-size:10.5px;letter-spacing:.32em;text-transform:uppercase;color:{accent};margin-bottom:18px;display:inline-flex;align-items:center;gap:14px}}
.jr-eyebrow::before,.jr-eyebrow::after{{content:'';width:24px;height:1px;background:{accent};opacity:.6}}
.jr-title{{font-family:{fhead};font-weight:300;font-size:clamp(38px,5.4vw,68px);line-height:1.04;letter-spacing:-.012em;color:{text};margin-bottom:18px}}
.jr-title i{{font-style:italic;color:{accent};font-weight:300}}
.jr-stand{{font-family:{fhead};font-style:italic;font-weight:300;font-size:clamp(15px,1.4vw,18px);line-height:1.55;color:{muted};max-width:560px;margin:0 auto}}
.jr-search-row{{display:flex;justify-content:center;margin:32px auto 0;max-width:480px;position:relative}}
.jr-search{{width:100%;background:transparent;border:none;border-bottom:1px solid {border};padding:10px 0 10px 28px;font-family:{fmono};font-size:11.5px;letter-spacing:.18em;text-transform:uppercase;color:{text};outline:none}}
.jr-search:focus{{border-bottom-color:{accent}}}
.jr-search::placeholder{{color:{muted};letter-spacing:.22em;font-size:10.5px;opacity:.7}}
.jr-search-row::before{{content:'';position:absolute;left:0;top:14px;width:14px;height:14px;border:1px solid {muted};border-radius:50%;opacity:.5}}
.jr-search-row::after{{content:'';position:absolute;left:11px;top:24px;width:6px;height:1px;background:{muted};transform:rotate(45deg);opacity:.5}}

/* Category nav - elegant inline links with hairline separators */
.jr-cats{{display:flex;justify-content:center;flex-wrap:wrap;gap:0;margin:48px 0 64px;border-top:1px solid {border};border-bottom:1px solid {border};padding:14px 0}}
.jr-cat{{font-family:{fmono};font-size:10px;letter-spacing:.24em;text-transform:uppercase;color:{muted};padding:6px 18px;background:none;border:none;cursor:pointer;font-family:{fmono};transition:color .25s;position:relative}}
.jr-cat:not(:last-child)::after{{content:'';position:absolute;right:0;top:50%;transform:translateY(-50%);width:1px;height:10px;background:{border}}}
.jr-cat:hover,.jr-cat.active{{color:{accent}}}
.jr-cat.active{{font-weight:600}}

/* FEATURE hero - full-width portrait image with overlaid editorial caption */
.jr-feature{{display:grid;grid-template-columns:1.05fr .95fr;gap:48px;margin-bottom:84px;align-items:center}}
.jr-feature-img{{aspect-ratio:5/4;overflow:hidden;background:{bg2};border:1px solid {border};position:relative}}
.jr-feature-img img{{width:100%;height:100%;object-fit:cover;transition:transform 1s cubic-bezier(.22,1,.36,1);filter:grayscale(.08) contrast(1.04)}}
.jr-feature:hover .jr-feature-img img{{transform:scale(1.04);filter:grayscale(0) contrast(1.06)}}
.jr-feature-body .jr-num{{font-family:{fmono};font-size:10px;letter-spacing:.28em;text-transform:uppercase;color:{accent};margin-bottom:18px;display:inline-flex;align-items:center;gap:14px}}
.jr-feature-body .jr-num::before{{content:'';width:38px;height:1px;background:{accent}}}
.jr-feature-cat{{font-family:{fhead};font-style:italic;font-weight:400;font-size:14px;color:{accent};margin-bottom:14px;letter-spacing:.005em}}
.jr-feature-h{{font-family:{fhead};font-weight:300;font-size:clamp(28px,3.4vw,46px);line-height:1.08;letter-spacing:-.012em;color:{text};margin-bottom:18px}}
.jr-feature-h a{{color:inherit;text-decoration:none}}
.jr-feature-stand{{font-family:{fhead};font-weight:300;font-size:17px;line-height:1.55;color:{muted};margin-bottom:24px;max-width:480px}}
.jr-feature-meta{{font-family:{fmono};font-size:10.5px;letter-spacing:.22em;text-transform:uppercase;color:{muted};padding-top:14px;border-top:1px solid {border}}}

/* 2-column editorial grid below the feature */
.jr-grid{{display:grid;grid-template-columns:repeat(2,1fr);gap:56px 48px;margin-bottom:64px}}
.jr-card{{display:block;color:inherit;text-decoration:none}}
.jr-card-img-wrap{{aspect-ratio:4/5;overflow:hidden;background:{bg2};border:1px solid {border};margin-bottom:22px;position:relative}}
.jr-card-img-wrap img{{width:100%;height:100%;object-fit:cover;transition:transform .9s cubic-bezier(.22,1,.36,1);filter:grayscale(.12) contrast(1.04)}}
.jr-card:hover .jr-card-img-wrap img{{transform:scale(1.05);filter:grayscale(0) contrast(1.06)}}
.jr-card-num{{font-family:{fmono};font-size:10px;letter-spacing:.22em;text-transform:uppercase;color:{accent};margin-bottom:10px;display:inline-flex;align-items:center;gap:10px}}
.jr-card-num::before{{content:'';width:24px;height:1px;background:{accent};opacity:.6}}
.jr-card-cat{{font-family:{fhead};font-style:italic;font-size:13.5px;color:{accent};margin-bottom:10px;letter-spacing:.005em}}
.jr-card-h{{font-family:{fhead};font-weight:400;font-size:clamp(20px,2vw,26px);line-height:1.15;letter-spacing:-.005em;color:{text};margin-bottom:12px}}
.jr-card-stand{{font-family:{fhead};font-weight:300;font-size:14.5px;line-height:1.55;color:{muted};margin-bottom:14px;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}}
.jr-card-meta{{font-family:{fmono};font-size:10px;letter-spacing:.22em;text-transform:uppercase;color:{muted};padding-top:12px;border-top:1px solid {border}}}

/* Page indicator - "N° 01 / 24" style instead of Prev/Next buttons */
.jr-page{{display:flex;justify-content:center;align-items:center;gap:36px;margin-top:48px;padding-top:32px;border-top:1px solid {border}}}
.jr-page-btn{{background:transparent;border:none;font-family:{fmono};font-size:10.5px;letter-spacing:.26em;text-transform:uppercase;color:{muted};cursor:pointer;padding:8px 0;transition:color .25s}}
.jr-page-btn:hover:not(:disabled){{color:{accent}}}
.jr-page-btn:disabled{{opacity:.3;cursor:not-allowed}}
.jr-page-num{{font-family:{fhead};font-style:italic;font-size:18px;color:{accent};letter-spacing:.02em;min-width:80px;text-align:center}}

.jr-empty{{text-align:center;padding:96px 24px;border:1px solid {border};background:{bg2}}}
.jr-empty-h{{font-family:{fhead};font-style:italic;font-weight:300;font-size:24px;color:{text};margin-bottom:10px}}
.jr-empty-p{{font-family:{fhead};font-weight:300;font-size:14px;color:{muted}}}

@media(max-width:960px){{
  .jr{{padding:36px 22px 80px}}
  .jr-feature{{grid-template-columns:1fr;gap:28px;margin-bottom:64px}}
  .jr-grid{{grid-template-columns:1fr;gap:48px}}
  .jr-cats{{margin:36px 0 48px;padding:10px 0}}
  .jr-cat{{padding:5px 12px;font-size:9.5px;letter-spacing:.2em}}
}}
@media(max-width:560px){{
  .jr{{padding:28px 18px 64px}}
  .jr-title{{font-size:clamp(28px,8vw,38px)}}
  .jr-feature-h{{font-size:clamp(24px,7vw,30px)}}
  .jr-card-h{{font-size:18px}}
  .jr-page{{gap:18px}}
}}"""

    body = f"""<main class="jr">
  <header class="jr-head">
    <div class="jr-eyebrow">The Journal</div>
    <h1 class="jr-title">A record of <i>quiet rooms</i>, considered light, and evenings that remain.</h1>
    <p class="jr-stand">Notes from the studio on the craft of atmosphere. Field reports, design close-reads, and the occasional letter from a private dinner where everything aligned.</p>
    <div class="jr-search-row">
      <input id="jr-search" class="jr-search" type="search" placeholder="Search entries">
    </div>
  </header>

  <nav class="jr-cats" id="jr-cats">
    <button class="jr-cat active" type="button" data-cat="__all__">All entries</button>
  </nav>

  <article class="jr-feature" id="jr-feature" style="display:none">
    <a class="jr-feature-img" id="jr-feat-img-link" href="#"><img id="jr-feat-img" loading="lazy" alt=""></a>
    <div class="jr-feature-body">
      <div class="jr-num" id="jr-feat-num">The latest entry</div>
      <div class="jr-feature-cat" id="jr-feat-cat"></div>
      <h2 class="jr-feature-h"><a id="jr-feat-link" href="#"></a></h2>
      <p class="jr-feature-stand" id="jr-feat-stand"></p>
      <div class="jr-feature-meta" id="jr-feat-meta"></div>
    </div>
  </article>

  <div class="jr-grid" id="jr-grid"></div>

  <nav class="jr-page" id="jr-page" style="display:none" aria-label="Pagination">
    <button id="jr-prev" class="jr-page-btn" type="button">&larr; Earlier</button>
    <span class="jr-page-num" id="jr-page-num"></span>
    <button id="jr-next" class="jr-page-btn" type="button">Later &rarr;</button>
  </nav>
</main>

<script>
(function(){{
  if(!document.getElementById('jr-grid'))return;
  var PER_PAGE=10;
  var FALLBACK_IMG={json.dumps(fallback_img)};
  var SITE_CAT={json.dumps(s.get('category') or 'Journal')};
  var all=[],activeCat='__all__',query='',page=1;
  var gridEl=document.getElementById('jr-grid');
  var featEl=document.getElementById('jr-feature');
  var catsEl=document.getElementById('jr-cats');
  var pageEl=document.getElementById('jr-page');
  var prevBtn=document.getElementById('jr-prev');
  var nextBtn=document.getElementById('jr-next');
  var pageNumEl=document.getElementById('jr-page-num');
  var searchEl=document.getElementById('jr-search');
  function esc(t){{return String(t==null?'':t).replace(/[&<>"']/g,function(c){{return({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}})[c];}});}}
  function href(p){{return './'+encodeURIComponent(p.slug||'').replace(/%2F/g,'/')+'/';}}
  function pad(n){{return n<10?'N° 0'+n:'N° '+n;}}
  function dateStr(iso){{if(!iso)return'';var d=new Date(iso);if(isNaN(d))return iso;return d.toLocaleDateString('en-GB',{{day:'2-digit',month:'short',year:'numeric'}}).toUpperCase();}}
  function filtered(){{
    var q=query.trim().toLowerCase();
    return all.filter(function(p){{
      if(activeCat!=='__all__'&&(p.category||SITE_CAT)!==activeCat)return false;
      if(q&&String(p.title||'').toLowerCase().indexOf(q)===-1&&String(p.meta_description||'').toLowerCase().indexOf(q)===-1)return false;
      return true;
    }});
  }}
  function renderFeature(arr){{
    if(!arr.length){{featEl.style.display='none';return;}}
    var lead=arr[0];
    var img=lead.image||FALLBACK_IMG;
    document.getElementById('jr-feat-img-link').setAttribute('href',href(lead));
    document.getElementById('jr-feat-img').src=img;
    document.getElementById('jr-feat-img').setAttribute('alt',lead.title||'');
    document.getElementById('jr-feat-img').onerror=function(){{this.onerror=null;this.src=FALLBACK_IMG;}};
    document.getElementById('jr-feat-cat').textContent=lead.category||SITE_CAT;
    var lk=document.getElementById('jr-feat-link');
    lk.setAttribute('href',href(lead));
    lk.textContent=lead.title||'Untitled';
    document.getElementById('jr-feat-stand').textContent=lead.meta_description||'';
    document.getElementById('jr-feat-meta').textContent=[dateStr(lead.date_iso),lead.author||''].filter(Boolean).join('  ·  ');
    featEl.style.display='grid';
  }}
  function renderGrid(arr){{
    var rest=arr.slice(1);
    var total=rest.length;
    var pages=Math.max(1,Math.ceil(total/PER_PAGE));
    if(page>pages)page=pages;
    var start=(page-1)*PER_PAGE;
    var slice=rest.slice(start,start+PER_PAGE);
    if(!arr.length){{
      gridEl.innerHTML='<div class="jr-empty"><div class="jr-empty-h">No entries match your filters</div><p class="jr-empty-p">Try clearing the search or picking a different category above.</p></div>';
      pageEl.style.display='none';
      return;
    }}
    gridEl.innerHTML=slice.map(function(p,i){{
      var n=pad(start+i+2); // +2 because feature is 01
      var img=p.image||FALLBACK_IMG;
      return '<a class="jr-card" href="'+href(p)+'">'+
        '<div class="jr-card-img-wrap"><img loading="lazy" alt="'+esc(p.title||'')+'" src="'+esc(img)+'" onerror="this.onerror=null;this.src=\\''+FALLBACK_IMG+'\\'"></div>'+
        '<div class="jr-card-num">'+n+'</div>'+
        '<div class="jr-card-cat">'+esc(p.category||SITE_CAT)+'</div>'+
        '<h3 class="jr-card-h">'+esc(p.title||'Untitled')+'</h3>'+
        '<p class="jr-card-stand">'+esc(p.meta_description||'')+'</p>'+
        '<div class="jr-card-meta">'+[dateStr(p.date_iso),p.author||''].filter(Boolean).join('  ·  ')+'</div>'+
      '</a>';
    }}).join('');
    if(pages>1){{
      pageEl.style.display='flex';
      pageNumEl.textContent=pad(page)+' / '+pad(pages);
      prevBtn.disabled=page<=1;
      nextBtn.disabled=page>=pages;
    }} else {{pageEl.style.display='none';}}
  }}
  function rerender(){{var arr=filtered();renderFeature(arr);renderGrid(arr);}}
  function setCat(c){{activeCat=c;page=1;Array.prototype.forEach.call(catsEl.querySelectorAll('.jr-cat'),function(b){{b.classList.toggle('active',b.getAttribute('data-cat')===c);}});rerender();}}
  catsEl.addEventListener('click',function(e){{var b=e.target.closest('.jr-cat');if(!b)return;setCat(b.getAttribute('data-cat'));}});
  var deb;
  searchEl.addEventListener('input',function(){{clearTimeout(deb);deb=setTimeout(function(){{query=searchEl.value;page=1;rerender();}},200);}});
  prevBtn.addEventListener('click',function(){{if(page>1){{page--;rerender();window.scrollTo({{top:0,behavior:'smooth'}});}}}});
  nextBtn.addEventListener('click',function(){{page++;rerender();window.scrollTo({{top:0,behavior:'smooth'}});}});
  // Archive page lives at /articles/index.html so ./articles.json resolves
  // to the wrong path. Try both: ../articles.json first (correct path), then
  // ./articles.json as a fallback for older deploys.
  function _fetchArts(){{
    return fetch('../articles.json',{{cache:'no-store'}}).then(function(r){{
      if(r.ok)return r.json();
      return fetch('./articles.json',{{cache:'no-store'}}).then(function(r2){{
        if(!r2.ok)throw 0; return r2.json();
      }});
    }});
  }}
  _fetchArts().then(function(data){{
    all=Array.isArray(data)?data.slice():[];
    all.sort(function(a,b){{return String(b.date_iso||'').localeCompare(String(a.date_iso||''));}});
    // Build categories from actual data
    var seen={{}};var cats=[];
    all.forEach(function(a){{var c=a.category||SITE_CAT;if(!seen[c]){{seen[c]=1;cats.push(c);}}}});
    cats.forEach(function(c){{
      var btn=document.createElement('button');
      btn.className='jr-cat';btn.type='button';btn.setAttribute('data-cat',c);btn.textContent=c;
      catsEl.appendChild(btn);
    }});
    rerender();
  }}).catch(function(){{
    gridEl.innerHTML='<div class="jr-empty"><div class="jr-empty-h">The journal opens soon</div><p class="jr-empty-p">New entries will appear here as they publish. Check back soon.</p></div>';
  }});
}})();
</script>"""
    return body, css


def _articles_body_performance(s):
    """Athletic / performance archive layout. Full-bleed dark hero with a
    big lime headline, sticky filter row, full-width 4-col card grid that
    drops to 3/2/1 cleanly. Opt-in via `performance_archive: true` in the
    site config; used by fitpulsepro and any other athletic / sports site.
    The visuals are tuned for a dark page with one bold accent color."""
    accent = s.get('primary') or '#d6ff3f'
    accent_alt = s.get('primary2') or accent
    bg     = s.get('bg') or '#0c0e14'
    bg2    = s.get('bg2') or '#13161e'
    surf   = s.get('surface') or '#1a1e28'
    text   = s.get('text') or '#f0f1f4'
    muted  = s.get('muted') or '#9aa0aa'
    border = s.get('brd') or 'rgba(255,255,255,.08)'
    fhead  = s.get('font_head') or "'Inter Tight','Inter',system-ui,sans-serif"
    fsans  = s.get('font_body') or "'Inter',system-ui,sans-serif"
    fmono  = s.get('font_mono') or "'JetBrains Mono',ui-monospace,monospace"
    fallback_img = ("https://images.unsplash.com/photo-1517836357463-d25dfeac3438"
                    "?w=1400&q=85&auto=format&fit=crop")

    css = f""".pf-wrap{{background:{bg};color:{text};margin:0;padding:0;font-family:{fsans};min-height:100vh}}
.pf-wrap *{{box-sizing:border-box}}
.pf-hero{{padding:84px 6vw 56px;max-width:100%;background:linear-gradient(180deg,{bg2} 0%,{bg} 100%);border-bottom:1px solid {border}}}
.pf-hero-row{{display:flex;align-items:flex-end;justify-content:space-between;gap:48px;flex-wrap:wrap;max-width:1640px;margin:0 auto}}
.pf-hero-left{{flex:1;min-width:280px}}
.pf-eyebrow{{font-family:{fmono};font-size:11px;letter-spacing:.32em;text-transform:uppercase;color:{accent};margin-bottom:18px;display:inline-flex;align-items:center;gap:14px}}
.pf-eyebrow::before{{content:'';display:inline-block;width:32px;height:2px;background:{accent}}}
.pf-h1{{font-family:{fhead};font-size:clamp(40px,7vw,96px);font-weight:700;line-height:.95;letter-spacing:-.028em;color:{text};margin:0 0 22px;max-width:1100px}}
.pf-h1 em{{font-style:normal;color:{accent}}}
.pf-stand{{font-size:clamp(15px,1.4vw,17px);color:{muted};max-width:620px;line-height:1.6}}
.pf-hero-stats{{display:flex;gap:36px;align-items:flex-end;flex-shrink:0}}
.pf-stat{{display:flex;flex-direction:column;gap:4px}}
.pf-stat-n{{font-family:{fhead};font-size:clamp(38px,5vw,64px);font-weight:700;letter-spacing:-.022em;color:{accent};line-height:1}}
.pf-stat-l{{font-family:{fmono};font-size:10px;letter-spacing:.28em;text-transform:uppercase;color:{muted}}}

/* Sticky filter row */
.pf-filters{{position:sticky;top:0;z-index:30;background:rgba(12,14,20,.92);backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px);border-bottom:1px solid {border};padding:18px 6vw}}
.pf-filters-row{{display:flex;align-items:center;gap:14px;max-width:1640px;margin:0 auto;flex-wrap:wrap}}
.pf-search{{position:relative;flex:1;min-width:200px;max-width:380px}}
.pf-search input{{width:100%;background:{surf};border:1px solid {border};border-radius:8px;padding:11px 14px 11px 38px;font-family:{fsans};font-size:13.5px;color:{text};outline:none;transition:border-color .2s}}
.pf-search input:focus{{border-color:{accent}}}
.pf-search input::placeholder{{color:{muted}}}
.pf-search::before{{content:'';position:absolute;left:14px;top:13px;width:14px;height:14px;border:1.5px solid {muted};border-radius:50%}}
.pf-search::after{{content:'';position:absolute;left:24px;top:24px;width:6px;height:1.5px;background:{muted};transform:rotate(45deg);transform-origin:left center}}
.pf-cats{{display:flex;gap:6px;flex-wrap:wrap;flex:2}}
.pf-cat{{font-family:{fmono};font-size:10px;letter-spacing:.18em;text-transform:uppercase;color:{muted};padding:8px 14px;background:transparent;border:1px solid {border};border-radius:999px;cursor:pointer;transition:color .2s,border-color .2s,background .2s}}
.pf-cat:hover{{color:{text};border-color:{accent}}}
.pf-cat.active{{color:{bg};background:{accent};border-color:{accent};font-weight:600}}
.pf-count{{font-family:{fmono};font-size:11px;letter-spacing:.18em;text-transform:uppercase;color:{muted};white-space:nowrap}}
.pf-count b{{color:{accent};font-weight:600}}

/* Main grid - full width */
.pf-grid-wrap{{padding:48px 6vw 96px;max-width:1640px;margin:0 auto}}
.pf-grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:24px}}
.pf-card{{position:relative;display:flex;flex-direction:column;background:{bg2};border:1px solid {border};border-radius:14px;overflow:hidden;text-decoration:none;color:{text};transition:transform .3s cubic-bezier(.22,1,.36,1),border-color .3s,box-shadow .3s}}
.pf-card:hover{{transform:translateY(-6px);border-color:{accent};box-shadow:0 24px 48px -24px rgba(0,0,0,.6),0 0 0 1px {accent}55}}
.pf-card-img{{position:relative;aspect-ratio:16/10;overflow:hidden;background:{surf}}}
.pf-card-img img{{width:100%;height:100%;object-fit:cover;transition:transform .8s cubic-bezier(.22,1,.36,1)}}
.pf-card:hover .pf-card-img img{{transform:scale(1.07)}}
.pf-card-badge{{position:absolute;top:12px;left:12px;background:{accent};color:{bg};font-family:{fmono};font-size:9.5px;letter-spacing:.18em;text-transform:uppercase;padding:5px 10px;border-radius:4px;font-weight:600}}
.pf-card-mins{{position:absolute;bottom:12px;right:12px;background:rgba(12,14,20,.9);color:{text};font-family:{fmono};font-size:10px;letter-spacing:.14em;text-transform:uppercase;padding:5px 10px;border-radius:4px;backdrop-filter:blur(4px)}}
.pf-card-body{{padding:22px 22px 24px;display:flex;flex-direction:column;flex:1}}
.pf-card-h{{font-family:{fhead};font-size:18px;font-weight:600;letter-spacing:-.015em;line-height:1.2;color:{text};margin:0 0 10px}}
.pf-card-excerpt{{font-size:13.5px;line-height:1.6;color:{muted};margin:0 0 16px;flex:1;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}}
.pf-card-foot{{display:flex;justify-content:space-between;align-items:center;padding-top:14px;border-top:1px solid {border}}}
.pf-card-date{{font-family:{fmono};font-size:10px;letter-spacing:.16em;text-transform:uppercase;color:{muted}}}
.pf-card-read{{font-family:{fmono};font-size:10px;letter-spacing:.2em;text-transform:uppercase;color:{accent};font-weight:600}}

.pf-loadmore-wrap{{grid-column:1/-1;text-align:center;margin-top:48px}}
.pf-loadmore{{background:transparent;border:1.5px solid {accent};color:{accent};font-family:{fmono};font-size:11px;letter-spacing:.28em;text-transform:uppercase;padding:18px 44px;cursor:pointer;border-radius:8px;font-weight:600;transition:background .25s,color .25s}}
.pf-loadmore:hover{{background:{accent};color:{bg}}}

.pf-empty{{grid-column:1/-1;text-align:center;padding:96px 24px;border:1px dashed {border};border-radius:14px;background:{bg2}}}
.pf-empty-h{{font-family:{fhead};font-size:24px;color:{text};margin-bottom:10px;font-weight:600}}
.pf-empty-p{{color:{muted};font-size:14px}}

@media(max-width:1200px){{.pf-grid{{grid-template-columns:repeat(3,1fr)}}}}
@media(max-width:880px){{
  .pf-grid{{grid-template-columns:repeat(2,1fr);gap:18px}}
  .pf-hero{{padding:60px 5vw 44px}}
  .pf-hero-row{{flex-direction:column;align-items:flex-start;gap:32px}}
  .pf-hero-stats{{gap:24px}}
  .pf-grid-wrap{{padding:36px 5vw 72px}}
}}
@media(max-width:560px){{
  .pf-grid{{grid-template-columns:1fr;gap:18px}}
  .pf-filters{{padding:14px 5vw}}
  .pf-filters-row{{gap:10px}}
  .pf-search{{max-width:100%}}
  .pf-cats{{gap:5px}}
  .pf-cat{{font-size:9px;padding:6px 10px}}
}}"""

    body = f"""<div class="pf-wrap">
  <section class="pf-hero">
    <div class="pf-hero-row">
      <div class="pf-hero-left">
        <div class="pf-eyebrow">The Archive</div>
        <h1 class="pf-h1">Train <em>smarter</em><br>not harder.</h1>
        <p class="pf-stand">Every plyometric protocol, strength template, and recovery study we've published. Filter by focus, search by topic, find what your next training block actually needs.</p>
      </div>
      <div class="pf-hero-stats">
        <div class="pf-stat"><span class="pf-stat-n" id="pf-stat-total">0</span><span class="pf-stat-l">Guides</span></div>
        <div class="pf-stat"><span class="pf-stat-n" id="pf-stat-cats">0</span><span class="pf-stat-l">Focus areas</span></div>
      </div>
    </div>
  </section>

  <nav class="pf-filters" aria-label="Filter">
    <div class="pf-filters-row">
      <div class="pf-search"><input id="pf-search" type="search" placeholder="Search guides…" aria-label="Search"></div>
      <div class="pf-cats" id="pf-cats"><button class="pf-cat active" type="button" data-cat="__all__">All</button></div>
      <div class="pf-count"><b id="pf-count-n">0</b> showing</div>
    </div>
  </nav>

  <div class="pf-grid-wrap"><div class="pf-grid" id="pf-grid"></div></div>
</div>

<script>
(function(){{
  if(!document.getElementById('pf-grid'))return;
  var PER_PAGE=12;
  var FALLBACK_IMG={json.dumps(fallback_img)};
  var SITE_CAT={json.dumps(s.get('category') or 'Guide')};
  var all=[],SHOWN=0,activeCat='__all__',query='';
  var gridEl=document.getElementById('pf-grid');
  var catsEl=document.getElementById('pf-cats');
  var searchEl=document.getElementById('pf-search');
  var countEl=document.getElementById('pf-count-n');
  var statTotal=document.getElementById('pf-stat-total');
  var statCats=document.getElementById('pf-stat-cats');
  function esc(t){{return String(t==null?'':t).replace(/[&<>"']/g,function(c){{return({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}})[c];}});}}
  function href(p){{return './'+encodeURIComponent(p.slug||'').replace(/%2F/g,'/')+'/';}}
  function dateStr(iso){{if(!iso)return'';var d=new Date(iso);if(isNaN(d))return iso;return d.toLocaleDateString('en-US',{{month:'short',day:'numeric',year:'numeric'}}).toUpperCase();}}
  function filtered(){{
    var q=query.trim().toLowerCase();
    return all.filter(function(p){{
      if(activeCat!=='__all__'&&(p.category||SITE_CAT)!==activeCat)return false;
      if(q&&String(p.title||'').toLowerCase().indexOf(q)===-1&&String(p.meta_description||'').toLowerCase().indexOf(q)===-1)return false;
      return true;
    }});
  }}
  function cardHTML(p){{
    var img=p.image||FALLBACK_IMG;
    return '<a class="pf-card" href="'+href(p)+'">'+
      '<div class="pf-card-img"><img loading="lazy" alt="'+esc(p.title||'')+'" src="'+esc(img)+'" onerror="this.onerror=null;this.src=\\''+FALLBACK_IMG+'\\'">'+
        '<span class="pf-card-badge">'+esc(p.category||SITE_CAT)+'</span>'+
        (p.mins?'<span class="pf-card-mins">'+p.mins+' min</span>':'')+
      '</div>'+
      '<div class="pf-card-body">'+
        '<h3 class="pf-card-h">'+esc(p.title||'Untitled')+'</h3>'+
        '<p class="pf-card-excerpt">'+esc(p.meta_description||'')+'</p>'+
        '<div class="pf-card-foot"><span class="pf-card-date">'+esc(dateStr(p.date_iso))+'</span><span class="pf-card-read">Read &rarr;</span></div>'+
      '</div>'+
    '</a>';
  }}
  function ensureLoadMore(arr){{
    var existing=document.getElementById('pf-loadmore-wrap');
    if(SHOWN>=arr.length){{if(existing)existing.remove();return;}}
    if(existing)return;
    var wrap=document.createElement('div');
    wrap.id='pf-loadmore-wrap';wrap.className='pf-loadmore-wrap';
    wrap.innerHTML='<button class="pf-loadmore" type="button">Load more guides</button>';
    gridEl.appendChild(wrap);
    wrap.querySelector('button').addEventListener('click',function(){{
      var next=Math.min(SHOWN+PER_PAGE,arr.length);
      var moreHTML=arr.slice(SHOWN,next).map(cardHTML).join('');
      wrap.insertAdjacentHTML('beforebegin',moreHTML);
      SHOWN=next;
      ensureLoadMore(arr);
    }});
  }}
  function render(){{
    var arr=filtered();
    countEl.textContent=arr.length;
    if(!arr.length){{
      gridEl.innerHTML='<div class="pf-empty"><div class="pf-empty-h">No matches</div><p class="pf-empty-p">Clear search or pick a different focus area.</p></div>';
      return;
    }}
    SHOWN=Math.min(PER_PAGE,arr.length);
    gridEl.innerHTML=arr.slice(0,SHOWN).map(cardHTML).join('');
    ensureLoadMore(arr);
  }}
  function setCat(c){{activeCat=c;Array.prototype.forEach.call(catsEl.querySelectorAll('.pf-cat'),function(b){{b.classList.toggle('active',b.getAttribute('data-cat')===c);}});render();}}
  catsEl.addEventListener('click',function(e){{var b=e.target.closest('.pf-cat');if(!b)return;setCat(b.getAttribute('data-cat'));}});
  var deb;
  searchEl.addEventListener('input',function(){{clearTimeout(deb);deb=setTimeout(function(){{query=searchEl.value;render();}},180);}});
  function fetchArts(){{
    return fetch('../articles.json',{{cache:'no-store'}}).then(function(r){{
      if(r.ok)return r.json();
      return fetch('./articles.json',{{cache:'no-store'}}).then(function(r2){{
        if(!r2.ok)throw 0; return r2.json();
      }});
    }});
  }}
  fetchArts().then(function(data){{
    all=Array.isArray(data)?data.slice():[];
    all.sort(function(a,b){{return String(b.date_iso||'').localeCompare(String(a.date_iso||''));}});
    statTotal.textContent=all.length;
    var seen={{}};var cats=[];
    all.forEach(function(a){{var c=a.category||SITE_CAT;if(!seen[c]){{seen[c]=1;cats.push(c);}}}});
    statCats.textContent=cats.length;
    cats.forEach(function(c){{
      var btn=document.createElement('button');btn.className='pf-cat';btn.type='button';btn.setAttribute('data-cat',c);btn.textContent=c;
      catsEl.appendChild(btn);
    }});
    render();
  }}).catch(function(){{
    gridEl.innerHTML='<div class="pf-empty"><div class="pf-empty-h">Archive opens soon</div><p class="pf-empty-p">New guides will appear here as they publish.</p></div>';
  }});
}})();
</script>"""
    return body, css


def _articles_body(s):
    """Build the body HTML (no chrome) for the All Articles page.
    Routes to the editorial luxury variant when the site config opts in via
    `editorial_archive: true`; otherwise emits the default news-style layout.
    Layout: compact hero row, news-style Latest feature block (5 newest),
    then the searchable categorized list + pager. Single fetch of articles.json
    shared across the feature block and the list."""
    if s.get('editorial_archive'):
        return _articles_body_editorial(s)
    if s.get('performance_archive'):
        return _articles_body_performance(s)
    ink     = _ink_for(s)
    on_ink  = s.get('bg') or '#0b0b0b'
    cats    = _articles_categories(s['id'])
    chips   = '\n        '.join(
        f'<button class="aa-chip" type="button" data-cat="{c}">{c}</button>'
        for c in cats
    )
    fallback_img = ("https://images.unsplash.com/photo-1499750310107-5fef28a66643"
                    "?w=600&q=80")

    css = f""".aa{{max-width:1080px;margin:0 auto;padding:clamp(22px,4vw,46px) clamp(16px,5vw,34px) 100px;font-family:inherit;color:{ink}}}
.aa *,.aa *::before,.aa *::after{{box-sizing:border-box}}
.aa-masthead{{padding-bottom:24px;margin-bottom:28px;border-bottom:1px solid {s['brd']}}}
.aa-mast-top{{display:flex;align-items:center;justify-content:space-between;gap:14px;flex-wrap:wrap;margin-bottom:14px}}
.aa-kicker{{font-size:11px;font-weight:800;letter-spacing:2.4px;text-transform:uppercase;color:{s['primary']}}}
.aa-count{{display:inline-block;background:{s['primary']};color:{on_ink};font-size:10px;font-weight:800;letter-spacing:.8px;text-transform:uppercase;padding:5px 12px;border-radius:999px;white-space:nowrap}}
.aa-title{{font-family:{s['font_head']};font-size:clamp(30px,5.4vw,52px);font-weight:800;line-height:1.04;letter-spacing:-.02em;margin:0 0 10px;color:{ink}}}
.aa-sub{{font-size:clamp(14px,1.6vw,16px);line-height:1.5;color:{s['muted']};margin:0 0 20px;max-width:60ch}}
.aa-search{{width:100%;background:{s['bg2']};border:1px solid {s['brd']};border-radius:12px;padding:14px 16px;font-size:15px;color:{ink};font-family:inherit;outline:none;transition:border-color .15s}}
.aa-search:focus{{border-color:{s['primary']}}}
.aa-latest{{margin:0 0 36px}}
.aa-latest-head{{display:flex;align-items:center;gap:12px;margin:0 0 16px}}
.aa-latest-label{{font-size:11px;font-weight:800;letter-spacing:2.2px;text-transform:uppercase;color:{s['primary']}}}
.aa-latest-rule{{flex:1;height:2px;background:{s['primary']};opacity:.22}}
.aa-latest-grid{{display:grid;grid-template-columns:1.4fr 1fr;gap:24px;align-items:start}}
.aa-lead{{display:block;background:{s['bg2']};border:1px solid {s['brd']};border-radius:14px;overflow:hidden;text-decoration:none;color:inherit;transition:border-color .15s,transform .15s}}
.aa-lead:hover{{transform:translateY(-2px);border-color:{s['primary']}}}
.aa-lead-img{{width:100%;height:clamp(200px,28vw,300px);object-fit:cover;background:{s['surface']};display:block}}
.aa-lead>div{{padding:18px 20px 20px}}
.aa-lead-cat{{font-size:10px;font-weight:800;letter-spacing:1.4px;text-transform:uppercase;color:{s['primary']};margin:0 0 8px}}
.aa-lead-h{{font-family:{s['font_head']};font-size:clamp(20px,2.5vw,28px);font-weight:800;line-height:1.18;letter-spacing:-.01em;color:inherit;margin:0 0 10px}}
.aa-lead-stand{{font-size:14px;line-height:1.6;color:{s['muted']};margin:0 0 12px;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}}
.aa-lead-meta{{font-size:11px;color:{s['muted']};letter-spacing:.4px}}
.aa-sec-col{{display:flex;flex-direction:column;gap:12px}}
.aa-sec{{display:grid;grid-template-columns:88px 1fr;gap:14px;padding:12px;background:{s['bg2']};border:1px solid {s['brd']};border-radius:12px;text-decoration:none;color:inherit;transition:border-color .15s,transform .15s}}
.aa-sec:hover{{border-color:{s['primary']};transform:translateY(-1px)}}
.aa-sec-img{{width:88px;height:72px;object-fit:cover;border-radius:8px;background:{s['surface']}}}
.aa-sec-body{{min-width:0;display:flex;flex-direction:column;justify-content:center}}
.aa-sec-h{{font-family:{s['font_head']};font-size:14px;font-weight:700;line-height:1.32;color:inherit;margin:0 0 5px;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}}
.aa-sec-date{{font-size:10px;color:{s['muted']};letter-spacing:.4px}}
.aa-controls{{margin:0 0 18px}}
.aa-chips{{display:flex;flex-wrap:wrap;gap:9px}}
.aa-chip{{background:{s['bg2']};border:1px solid {s['brd']};color:{s['muted']};font-size:12px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;padding:9px 16px;border-radius:999px;cursor:pointer;font-family:inherit;transition:all .15s;white-space:nowrap}}
.aa-chip:hover{{color:{ink};border-color:{s['primary']}}}
.aa-chip.active{{background:{s['primary']};color:{on_ink};border-color:{s['primary']}}}
.aa-meta{{font-size:12px;color:{s['muted']};margin:0 0 16px;letter-spacing:.3px}}
.aa-list{{display:grid;grid-template-columns:1fr;gap:16px}}
.aa-card{{display:grid;grid-template-columns:220px 1fr;gap:20px;background:{s['bg2']};border:1px solid {s['brd']};border-radius:14px;padding:16px;text-decoration:none;color:inherit;transition:border-color .15s,transform .15s}}
.aa-card:hover{{border-color:{s['primary']};transform:translateY(-2px)}}
.aa-thumb{{width:100%;height:140px;border-radius:10px;object-fit:cover;background:{s['surface']};display:block}}
.aa-body{{display:flex;flex-direction:column;justify-content:center;min-width:0}}
.aa-cat{{display:inline-block;font-size:10px;font-weight:800;letter-spacing:1px;text-transform:uppercase;color:{s['primary']};margin-bottom:7px}}
.aa-h{{font-family:{s['font_head']};font-size:clamp(16px,2vw,19px);font-weight:700;color:inherit;margin:0 0 7px;line-height:1.3}}
.aa-desc{{font-size:13.5px;line-height:1.6;color:{s['muted']};margin:0 0 9px;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}}
.aa-date{{font-size:11px;color:{s['muted']};letter-spacing:.4px}}
.aa-empty{{text-align:center;padding:64px 24px;color:{s['muted']};font-size:14px;background:{s['bg2']};border:1px dashed {s['brd']};border-radius:14px}}
.aa-pager{{display:flex;justify-content:center;align-items:center;gap:12px;margin-top:36px}}
.aa-pager button{{background:{s['bg2']};border:1px solid {s['brd']};color:{ink};font-size:12px;font-weight:700;letter-spacing:.5px;text-transform:uppercase;padding:10px 18px;border-radius:999px;cursor:pointer;font-family:inherit;transition:border-color .15s}}
.aa-pager button:hover:not(:disabled){{border-color:{s['primary']}}}
.aa-pager button:disabled{{opacity:.4;cursor:not-allowed}}
.aa-pager .aa-page-num{{font-size:12px;color:{s['muted']};font-weight:700}}
.aa-footer-kicker{{margin-top:52px;padding-top:26px;border-top:1px solid {s['brd']};display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:14px}}
.aa-kicker-label{{font-size:11px;font-weight:800;text-transform:uppercase;letter-spacing:2.2px;color:{s['primary']}}}
.aa-back-home{{font-size:12px;font-weight:600;color:{s['muted']};text-decoration:none;letter-spacing:.3px;transition:color .15s}}
.aa-back-home:hover{{color:{s['primary']}}}
@media(max-width:820px){{.aa-latest-grid{{grid-template-columns:1fr;gap:18px}}}}
@media(max-width:600px){{
  .aa-card{{grid-template-columns:1fr;gap:0;padding:0;overflow:hidden}}
  .aa-thumb{{height:188px;border-radius:0}}
  .aa-body{{padding:15px 16px 17px}}
  .aa-sec{{grid-template-columns:72px 1fr}}
  .aa-sec-img{{width:72px;height:64px}}
  .aa-chips{{flex-wrap:nowrap;overflow-x:auto;-webkit-overflow-scrolling:touch;padding-bottom:5px;margin-bottom:-5px;scrollbar-width:none}}
  .aa-chips::-webkit-scrollbar{{display:none}}
}}"""

    body = f"""<main class="aa">
  <header class="aa-masthead">
    <div class="aa-mast-top">
      <span class="aa-kicker">The Archive</span>
      <span class="aa-count" id="aa-count">0 published</span>
    </div>
    <h1 class="aa-title">All Articles</h1>
    <p class="aa-sub">Every report and analysis from {s['name']}, newest first.</p>
    <input id="aa-search" class="aa-search" type="search" placeholder="Search articles by title..." aria-label="Search articles">
  </header>
  <section class="aa-latest" id="aa-latest" style="display:none">
    <div class="aa-latest-head">
      <span class="aa-latest-label">Latest</span>
      <span class="aa-latest-rule"></span>
    </div>
    <div class="aa-latest-grid">
      <a class="aa-lead" id="aa-lead" href="#"></a>
      <div class="aa-sec-col" id="aa-sec-col"></div>
    </div>
  </section>
  <div class="aa-controls">
    <div class="aa-chips" id="aa-chips">
      <button class="aa-chip active" type="button" data-cat="__all__">All</button>
        {chips}
    </div>
  </div>
  <div class="aa-meta" id="aa-meta">Loading articles...</div>
  <div class="aa-list" id="all-list"></div>
  <div class="aa-pager" id="aa-pager" style="display:none">
    <button id="aa-prev" type="button">Prev</button>
    <span class="aa-page-num" id="aa-page-num">Page 1</span>
    <button id="aa-next" type="button">Next</button>
  </div>
  <div class="aa-footer-kicker">
    <span class="aa-kicker-label">ALL ARTICLES &middot; {s['name']}</span>
    <a href="./" class="aa-back-home">&larr; Back to home</a>
  </div>
</main>
<script>
(function(){{
  if(!document.getElementById('all-list'))return;
  var PER_PAGE=24;
  var FALLBACK_IMG='{fallback_img}';
  var SITE_CAT={json.dumps(s['category'])};
  var listEl=document.getElementById('all-list');
  var metaEl=document.getElementById('aa-meta');
  var countEl=document.getElementById('aa-count');
  var pagerEl=document.getElementById('aa-pager');
  var prevBtn=document.getElementById('aa-prev');
  var nextBtn=document.getElementById('aa-next');
  var pageNumEl=document.getElementById('aa-page-num');
  var searchEl=document.getElementById('aa-search');
  var chipsEl=document.getElementById('aa-chips');
  var latestEl=document.getElementById('aa-latest');
  var leadEl=document.getElementById('aa-lead');
  var secCol=document.getElementById('aa-sec-col');
  // Honor ?cat=... and ?q=... query params so cards/links elsewhere
  // on the site can deep-link to a filtered or searched view.
  var _params=new URLSearchParams(window.location.search);
  var _initialCat=_params.get('cat')||'__all__';
  var _initialQ=_params.get('q')||'';
  var all=[],activeCat=_initialCat,query=_initialQ,page=1;
  if(_initialQ){{searchEl.value=_initialQ;}}
  function escapeHtml(t){{return String(t==null?'':t).replace(/[&<>"']/g,function(c){{return({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}})[c];}});}}
  function slugHref(p){{return './'+encodeURIComponent(p.slug||'').replace(/%2F/g,'/')+'/';}}
  // Fuzzy match: a card category like "Europe" should match articles
  // tagged "Europe", "European Travel", or any cat containing the token.
  function catMatches(articleCat, filterCat){{
    if(filterCat==='__all__')return true;
    if(!articleCat)return false;
    var a=String(articleCat).toLowerCase(), f=String(filterCat).toLowerCase();
    return a===f||a.indexOf(f)!==-1||f.indexOf(a)!==-1;
  }}
  function filtered(){{
    var q=query.trim().toLowerCase();
    return all.filter(function(p){{
      if(!catMatches(p.category||SITE_CAT, activeCat))return false;
      if(q&&String(p.title||'').toLowerCase().indexOf(q)===-1)return false;
      return true;
    }});
  }}
  function renderLatest(){{
    if(!all.length){{latestEl.style.display='none';return;}}
    var feat=all.slice(0,5);
    var lead=feat[0];
    leadEl.setAttribute('href',slugHref(lead));
    leadEl.innerHTML='<img class="aa-lead-img" loading="lazy" alt="" src="'+escapeHtml(lead.image||FALLBACK_IMG)+'" onerror="this.onerror=null;this.src=\\''+FALLBACK_IMG+'\\'">'+
      '<div><div class="aa-lead-cat">'+escapeHtml(lead.category||SITE_CAT)+'</div>'+
      '<h2 class="aa-lead-h">'+escapeHtml(lead.title||'Untitled')+'</h2>'+
      '<p class="aa-lead-stand">'+escapeHtml(lead.meta_description||'')+'</p>'+
      '<div class="aa-lead-meta">'+escapeHtml(lead.date_iso||'')+(lead.author?' - '+escapeHtml(lead.author):'')+'</div></div>';
    secCol.innerHTML=feat.slice(1).map(function(p){{
      return '<a class="aa-sec" href="'+slugHref(p)+'">'+
        '<img class="aa-sec-img" loading="lazy" alt="" src="'+escapeHtml(p.image||FALLBACK_IMG)+'" onerror="this.onerror=null;this.src=\\''+FALLBACK_IMG+'\\'">'+
        '<div class="aa-sec-body"><h3 class="aa-sec-h">'+escapeHtml(p.title||'Untitled')+'</h3>'+
        '<span class="aa-sec-date">'+escapeHtml(p.date_iso||'')+'</span></div></a>';
    }}).join('');
    latestEl.style.display='block';
  }}
  function render(){{
    var arr=filtered();
    var total=arr.length;
    var pages=Math.max(1,Math.ceil(total/PER_PAGE));
    if(page>pages)page=pages;
    var start=(page-1)*PER_PAGE;
    var slice=arr.slice(start,start+PER_PAGE);
    if(!total){{
      listEl.innerHTML='<div class="aa-empty">No articles match your filters.</div>';
      pagerEl.style.display='none';
    }} else {{
      listEl.innerHTML=slice.map(function(p){{
        var img=p.image||FALLBACK_IMG;
        var cat=escapeHtml(p.category||SITE_CAT);
        var title=escapeHtml(p.title||'Untitled');
        var desc=escapeHtml(p.meta_description||'');
        var date=escapeHtml(p.date_iso||'');
        return '<a class="aa-card" href="'+slugHref(p)+'">'+
          '<img class="aa-thumb" loading="lazy" alt="" src="'+escapeHtml(img)+'" onerror="this.onerror=null;this.src=\\''+FALLBACK_IMG+'\\'">'+
          '<div class="aa-body"><span class="aa-cat">'+cat+'</span>'+
          '<h3 class="aa-h">'+title+'</h3>'+
          '<p class="aa-desc">'+desc+'</p>'+
          '<span class="aa-date">'+date+'</span></div></a>';
      }}).join('');
      pagerEl.style.display=pages>1?'flex':'none';
      pageNumEl.textContent='Page '+page+' of '+pages;
      prevBtn.disabled=page<=1;
      nextBtn.disabled=page>=pages;
    }}
    metaEl.textContent='Showing '+slice.length+' of '+all.length;
  }}
  function setCat(c){{activeCat=c;page=1;Array.prototype.forEach.call(chipsEl.querySelectorAll('.aa-chip'),function(b){{b.classList.toggle('active',b.getAttribute('data-cat')===c);}});render();}}
  // Apply the chip-active styling for the initial cat from URL ?cat=
  if(_initialCat!=='__all__'){{Array.prototype.forEach.call(chipsEl.querySelectorAll('.aa-chip'),function(b){{var dc=b.getAttribute('data-cat');b.classList.toggle('active', dc===_initialCat||(dc&&_initialCat&&(dc.toLowerCase().indexOf(_initialCat.toLowerCase())!==-1||_initialCat.toLowerCase().indexOf(dc.toLowerCase())!==-1)));}});}}
  chipsEl.addEventListener('click',function(e){{var b=e.target.closest('.aa-chip');if(!b)return;setCat(b.getAttribute('data-cat'));}});
  var deb;
  searchEl.addEventListener('input',function(){{clearTimeout(deb);deb=setTimeout(function(){{query=searchEl.value;page=1;render();}},200);}});
  prevBtn.addEventListener('click',function(){{if(page>1){{page--;render();window.scrollTo({{top:0,behavior:'smooth'}});}}}});
  nextBtn.addEventListener('click',function(){{page++;render();window.scrollTo({{top:0,behavior:'smooth'}});}});
  // The archive lives at /articles/index.html, so the data file is one level
  // up at ../articles.json. Try that first, fall back to ./articles.json for
  // any older flat deploys.
  function _loadAA(){{return fetch('../articles.json',{{cache:'no-store'}}).then(function(r){{if(r.ok)return r.json();return fetch('./articles.json',{{cache:'no-store'}}).then(function(r2){{if(!r2.ok)throw 0;return r2.json();}});}});}}
  _loadAA().then(function(data){{
    all=Array.isArray(data)?data.slice():[];
    all.sort(function(a,b){{return String(b.date_iso||'').localeCompare(String(a.date_iso||''));}});
    countEl.textContent=all.length+' published';
    if(!all.length){{
      listEl.innerHTML='<div class="aa-empty">No articles published yet.</div>';
      metaEl.textContent='Showing 0 of 0';
      return;
    }}
    renderLatest();
    render();
  }}).catch(function(){{
    countEl.textContent='0 published';
    listEl.innerHTML='<div class="aa-empty">No articles published yet.</div>';
    metaEl.textContent='Showing 0 of 0';
  }});
}})();
</script>"""
    # ── OnlineBiz Pro: distinct dark "operator index" skin ───────────────────
    # The all-articles body is injected into the homepage shell, so we can lean
    # on the homepage's own CSS variables (--accent2 purple, --lime, --display
    # Space Grotesk, --bg2/--surface/--border) for guaranteed alignment. These
    # rules are appended last so they win over the theme-driven defaults above.
    if s.get('id') in ('onlinebiz-pro', 'onlinebizpro'):
        css += """
.aa{font-family:'Inter',system-ui,sans-serif}
.aa-hero{border-bottom:1px solid var(--border,#222229)}
.aa-search{background:var(--bg2,#0d0d10);border:1px solid var(--border,#222229);color:var(--text,#f4f4f6);border-radius:10px}
.aa-search:focus{border-color:var(--accent2,#a78bfa);box-shadow:0 0 0 3px rgba(167,139,250,.15)}
.aa-count{background:linear-gradient(120deg,var(--accent2,#a78bfa),var(--lime,#bef264));color:#0a0a0b;font-weight:800}
.aa-latest-head{border-bottom:2px solid var(--accent2,#a78bfa)}
.aa-latest-label{font-family:'Space Grotesk','Inter',sans-serif;color:var(--lime,#bef264);letter-spacing:2.2px}
.aa-lead,.aa-sec,.aa-card{background:var(--bg2,#0d0d10);border:1px solid var(--border,#222229);border-radius:14px}
.aa-lead{border-left:3px solid;border-image:linear-gradient(180deg,var(--accent2,#a78bfa),var(--lime,#bef264)) 1}
.aa-lead:hover,.aa-card:hover{border-color:var(--accent2,#a78bfa);box-shadow:0 20px 50px -30px rgba(108,92,231,.7)}
.aa-sec:hover{border-color:var(--accent2,#a78bfa)}
.aa-lead-cat,.aa-cat{color:var(--lime,#bef264);font-weight:800}
.aa-lead-h,.aa-h,.aa-sec-h{font-family:'Space Grotesk','Inter',sans-serif;color:var(--text,#f4f4f6)}
.aa-chip{background:var(--bg2,#0d0d10);border:1px solid var(--border,#222229);color:var(--muted,#8b8b97);font-family:'Space Grotesk','Inter',sans-serif}
.aa-chip:hover{color:var(--text,#f4f4f6);border-color:var(--accent2,#a78bfa)}
.aa-chip.active{background:linear-gradient(120deg,var(--accent2,#a78bfa),var(--lime,#bef264));color:#0a0a0b;border-color:transparent}
.aa-pager button{background:var(--bg2,#0d0d10);border:1px solid var(--border,#222229);color:var(--text,#f4f4f6);font-family:'Space Grotesk','Inter',sans-serif}
.aa-pager button:hover:not(:disabled){border-color:var(--accent2,#a78bfa)}
.aa-kicker-label{font-family:'Space Grotesk','Inter',sans-serif;color:var(--lime,#bef264)}
.aa-back-home:hover{color:var(--accent2,#a78bfa)}
.aa-footer-kicker{border-top:1px solid var(--border,#222229)}
/* Beat the shell's light-paper contrast-audit (forces bare h1/h2/h3 dark on
   article-depth pages) so headings stay light on this dark archive. */
body[data-page-depth="1"] .aa-lead-h,
body[data-page-depth="1"] .aa-h,
body[data-page-depth="1"] .aa-sec-h{color:var(--text,#f4f4f6)!important}
"""
    return body, css


def gen_articles_index(s):
    """All-Articles index page wrapped in the homepage shell. Categorized chips,
    debounced search, paginated list rendered client-side from articles.json."""
    body, css = _articles_body(s)
    desc = f"All articles from {s['name']}. {s['footer_desc']}"
    return layout_shell.wrap_page(
        s['id'], title=f"All Articles - {s['name']}",
        description=desc, body_html=body, extra_css=css, depth=0,
    )


# ─────────────────────────────────────────────────────────────────────────────
# SPORTIQ PRO   -  ESPN/The Athletic dark sports editorial
# ─────────────────────────────────────────────────────────────────────────────
def sportiqpro_index(s):
    pxjs   = _pexels_js(s)
    about  = _about_block(s, s['bg2'], s['brd'], s['text'], s['muted'], s['primary'])
    seed   = abs(hash(s['id'])) % 1000
    domain = s.get('domain', f"siavashsed.github.io/{s['id']}")
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{s['name']}  -  {s['tagline']}</title>
<meta name="description" content="{s['hero_sub']}">
<link rel="canonical" href="https://{domain}/">
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
:root{{--bg:{s['bg']};--bg2:{s['bg2']};--surf:{s['surface']};--text:{s['text']};--muted:{s['muted']};--red:{s['primary']};--brd:{s['brd']}}}
body{{background:var(--bg);color:var(--text);font-family:'Inter',system-ui,sans-serif;line-height:1.6}}
a{{color:inherit;text-decoration:none}}
img{{max-width:100%;display:block}}
/* NAV */
#nav{{position:sticky;top:0;z-index:100;background:rgba(15,15,18,.97);border-bottom:2px solid var(--red);backdrop-filter:blur(8px)}}
.nav-inner{{max-width:1280px;margin:0 auto;padding:0 20px;height:56px;display:flex;align-items:center;gap:24px}}
.nav-logo{{font-size:20px;font-weight:900;letter-spacing:-1px;color:var(--text);text-transform:uppercase;flex-shrink:0}}
.nav-logo span{{color:var(--red)}}
.nav-links{{display:flex;gap:4px;flex:1}}
.nav-links a{{font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:.8px;color:var(--muted);padding:6px 12px;border-radius:4px;transition:all .15s}}
.nav-links a:hover{{color:var(--text);background:rgba(239,68,68,.1)}}
.nav-date{{font-size:11px;color:var(--muted);flex-shrink:0}}
/* TICKER */
#ticker{{background:var(--red);padding:6px 0;overflow:hidden}}
.ticker-inner{{display:flex;align-items:center;white-space:nowrap;font-size:11px;font-weight:700;letter-spacing:.5px;text-transform:uppercase;color:#fff;gap:32px;animation:tickerScroll 30s linear infinite}}
@keyframes tickerScroll{{from{{transform:translateX(0)}}to{{transform:translateX(-50%)}}}}
/* HERO */
#hero{{position:relative;height:520px;overflow:hidden;background:var(--bg2)}}
#hero-img{{width:100%;height:100%;object-fit:cover;opacity:0;transition:opacity .8s;display:block}}
#hero-overlay{{position:absolute;inset:0;background:linear-gradient(to top,rgba(0,0,0,.9) 0%,rgba(0,0,0,.3) 60%,transparent 100%)}}
#hero-content{{position:absolute;bottom:0;left:0;right:0;padding:32px 40px}}
.hero-tag{{display:inline-block;background:var(--red);color:#fff;font-size:10px;font-weight:800;text-transform:uppercase;letter-spacing:1px;padding:3px 10px;border-radius:3px;margin-bottom:12px}}
.hero-title{{font-size:clamp(24px,4vw,42px);font-weight:900;line-height:1.15;margin-bottom:10px;max-width:720px;text-shadow:0 2px 8px rgba(0,0,0,.8)}}
.hero-desc{{font-size:15px;color:rgba(255,255,255,.8);max-width:560px;margin-bottom:16px;line-height:1.5}}
.hero-btn{{display:inline-block;background:var(--red);color:#fff;font-size:12px;font-weight:800;text-transform:uppercase;letter-spacing:.8px;padding:10px 22px;border-radius:4px}}
/* LAYOUT */
.wrap{{max-width:1280px;margin:0 auto;padding:40px 20px}}
.main-grid{{display:grid;grid-template-columns:1fr 320px;gap:40px;align-items:start}}
/* ARTICLE CARDS */
.section-label{{font-size:10px;font-weight:800;text-transform:uppercase;letter-spacing:2px;color:var(--red);margin-bottom:16px;padding-bottom:8px;border-bottom:2px solid var(--red)}}
.feat-card{{background:var(--surf);border-radius:8px;overflow:hidden;margin-bottom:24px;border:1px solid var(--brd)}}
.feat-card img{{width:100%;height:220px;object-fit:cover}}
.feat-card-body{{padding:20px}}
.feat-tag{{font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.8px;color:var(--red);margin-bottom:8px}}
.feat-title{{font-size:20px;font-weight:800;line-height:1.3;margin-bottom:8px}}
.feat-meta{{font-size:11px;color:var(--muted)}}
.h-card{{display:flex;gap:14px;padding:14px 0;border-bottom:1px solid var(--brd)}}
.h-card:last-child{{border-bottom:none}}
.h-card img{{width:100px;height:70px;object-fit:cover;border-radius:5px;flex-shrink:0}}
.h-card-body{{flex:1}}
.h-card-tag{{font-size:9px;font-weight:700;text-transform:uppercase;color:var(--red);margin-bottom:4px}}
.h-card-title{{font-size:13px;font-weight:700;line-height:1.35;margin-bottom:4px}}
.h-card-meta{{font-size:10px;color:var(--muted)}}
/* SIDEBAR */
.sidebar-box{{background:var(--surf);border-radius:8px;padding:16px;border:1px solid var(--brd);margin-bottom:20px}}
.sidebar-label{{font-size:10px;font-weight:800;text-transform:uppercase;letter-spacing:1.5px;color:var(--red);margin-bottom:12px}}
.side-item{{padding:10px 0;border-bottom:1px solid var(--brd);font-size:12px;font-weight:600;line-height:1.4}}
.side-item:last-child{{border-bottom:none}}
.side-num{{font-size:18px;font-weight:900;color:var(--red);margin-right:8px;line-height:1}}
.nl-box{{background:linear-gradient(135deg,var(--red) 0%,{s['primary2']} 100%);border-radius:8px;padding:20px;color:#fff}}
.nl-box h4{{font-size:14px;font-weight:800;margin-bottom:4px}}
.nl-box p{{font-size:12px;opacity:.85;margin-bottom:12px;line-height:1.5}}
.nl-input{{width:100%;padding:8px 12px;border:none;border-radius:4px;font-size:12px;margin-bottom:8px}}
.nl-btn{{width:100%;background:#fff;color:var(--red);font-size:12px;font-weight:800;text-transform:uppercase;letter-spacing:.5px;border:none;padding:8px;border-radius:4px;cursor:pointer}}
/* MORE GRID */
.more-grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:20px;margin-top:40px}}
.grid-card{{background:var(--surf);border-radius:8px;overflow:hidden;border:1px solid var(--brd)}}
.grid-card img{{width:100%;height:140px;object-fit:cover}}
.grid-card-body{{padding:12px}}
.grid-tag{{font-size:9px;font-weight:700;text-transform:uppercase;color:var(--red);margin-bottom:5px}}
.grid-title{{font-size:13px;font-weight:700;line-height:1.35;margin-bottom:5px}}
.grid-meta{{font-size:10px;color:var(--muted)}}
/* FOOTER */
#foot{{background:#000;padding:32px 20px;margin-top:60px;border-top:2px solid var(--red)}}
.foot-inner{{max-width:1280px;margin:0 auto;display:flex;flex-wrap:wrap;gap:24px;justify-content:space-between;align-items:center}}
.foot-logo{{font-size:18px;font-weight:900;text-transform:uppercase}}
.foot-logo span{{color:var(--red)}}
.foot-links{{display:flex;gap:16px;flex-wrap:wrap}}
.foot-links a{{font-size:11px;color:var(--muted);transition:color .15s}}
.foot-links a:hover{{color:var(--text)}}
.foot-copy{{font-size:11px;color:var(--muted);width:100%;text-align:center;margin-top:16px;padding-top:16px;border-top:1px solid var(--brd)}}
/* RESPONSIVE */
@media(max-width:900px){{.main-grid{{grid-template-columns:1fr}}.sidebar-box:last-child{{display:none}}.more-grid{{grid-template-columns:repeat(2,1fr)}}.nav-links{{display:none}}.hero-content{{padding:20px}}}}
@media(max-width:600px){{.more-grid{{grid-template-columns:1fr}}.hero-title{{font-size:22px}}.feat-card img{{height:170px}}}}
</style>
</head>
<body>

<!-- NAV -->
<nav id="nav">
  <div class="nav-inner">
    <div class="nav-logo"><span>Sport</span>IQ Pro</div>
    <div class="nav-links">
      <a href="#">Training</a>
      <a href="#">Recovery</a>
      <a href="#">Nutrition</a>
      <a href="#">Coaching</a>
      <a href="#">Research</a>
      <a href="about.html">About</a>
    </div>
    <div class="nav-date" id="nav-date"></div>
  </div>
</nav>

<!-- TICKER -->
<div id="ticker"><div class="ticker-inner" id="ticker-inner">Loading latest…</div></div>

<!-- HERO -->
<div id="hero">
  <img id="hero-img" src="" alt="">
  <div id="hero-overlay"></div>
  <div id="hero-content">
    <div class="hero-tag" id="hero-tag">Featured</div>
    <div class="hero-title" id="hero-title">Loading…</div>
    <div class="hero-desc" id="hero-desc"></div>
    <a id="hero-link" href="#" class="hero-btn">Read Full Article →</a>
  </div>
</div>

<!-- MAIN -->
<div class="wrap">
  <div class="main-grid">
    <div>
      <div class="section-label">Latest</div>
      <div id="feat-card-wrap"></div>
      <div id="h-card-list"></div>
    </div>
    <div>
      <div class="sidebar-box">
        <div class="sidebar-label">Top Reads</div>
        <div id="side-list"></div>
      </div>
      <div class="nl-box">
        <h4>{s['nl_head']}</h4>
        <p>{s['nl_sub']}</p>
        <input class="nl-input" type="email" placeholder="your@email.com">
        <button class="nl-btn">Subscribe Free</button>
      </div>
    </div>
  </div>

  <div class="section-label" style="margin-top:40px">More Articles</div>
  <div class="more-grid" id="more-grid"></div>
</div>

{about}

<!-- FOOTER -->
<footer id="foot">
  <div class="foot-inner">
    <div class="foot-logo"><span>Sport</span>IQ Pro</div>
    <div class="foot-links">
      <a href="about.html">About</a>
      <a href="privacy.html">Privacy</a>
      <a href="terms.html">Terms</a>
    </div>
    <div class="foot-copy">© {s['name']}. {s['footer_desc']}</div>
  </div>
</footer>

<script>
document.getElementById('nav-date').textContent = new Date().toLocaleDateString('en-US',{{weekday:'long',month:'long',day:'numeric'}});
var CATS=['Training','Recovery','Nutrition','Coaching','Research','Programming'];
function cat(i){{return CATS[i%CATS.length];}}
function fmt(d){{try{{return new Date(d).toLocaleDateString('en-US',{{month:'short',day:'numeric',year:'numeric'}});}}catch(e){{return '';}}}}
function picUrl(slug,w,h){{var seed=Math.abs(slug.split('').reduce(function(a,c){{return a+c.charCodeAt(0);}},0))%1000;return 'https://picsum.photos/seed/siq'+seed+'/'+w+'/'+h;}}

function render(posts){{
  if(!posts||!posts.length)return;
  var p0=posts[0];
  document.getElementById('hero-tag').textContent=cat(0);
  document.getElementById('hero-title').textContent=p0.title||'';
  document.getElementById('hero-desc').textContent=p0.meta_description||'';
  document.getElementById('hero-link').href=(p0.slug||'#')+'/';
  var heroImg=document.getElementById('hero-img');
  heroImg.onload=function(){{heroImg.style.opacity='1';}};
  heroImg.src=p0.image||picUrl(p0.slug||'hero',1400,520);

  // Ticker
  var titles=posts.slice(0,8).map(function(p,i){{return '<span style="color:rgba(255,255,255,.5);margin-right:8px">►</span>'+p.title;}});
  var full=titles.concat(titles).join('<span style="margin:0 24px;opacity:.4">·</span>');
  document.getElementById('ticker-inner').innerHTML=full;

  // Featured card (post 1)
  var p1=posts[1]||{{}};
  document.getElementById('feat-card-wrap').innerHTML=p1.title?
    '<div class="feat-card"><a href="'+(p1.slug||'#')+'/">'+'<img src="'+(p1.image||picUrl(p1.slug||'f1',600,220))+'" alt="" loading="lazy"></a><div class="feat-card-body"><div class="feat-tag">'+cat(1)+'</div><div class="feat-title"><a href="'+(p1.slug||'#')+'/">'+p1.title+'</a></div><div class="feat-meta">'+fmt(p1.date_iso)+' · '+'{s['author']}'+'</div></div></div>':'';

  // Horizontal cards (posts 2-4)
  var hList=document.getElementById('h-card-list');
  hList.innerHTML=posts.slice(2,5).map(function(p,i){{
    return '<div class="h-card"><a href="'+(p.slug||'#')+'/"><img src="'+(p.image||picUrl(p.slug||'h'+i,200,140))+'" alt="" loading="lazy"></a><div class="h-card-body"><div class="h-card-tag">'+cat(i+2)+'</div><div class="h-card-title"><a href="'+(p.slug||'#')+'/">'+p.title+'</a></div><div class="h-card-meta">'+fmt(p.date_iso)+'</div></div></div>';
  }}).join('');

  // Sidebar (posts 5-9)
  document.getElementById('side-list').innerHTML=posts.slice(5,10).map(function(p,i){{
    return '<div class="side-item"><span class="side-num">'+(i+1)+'</span><a href="'+(p.slug||'#')+'/">'+p.title+'</a></div>';
  }}).join('');

  // More grid (posts 10-13)
  document.getElementById('more-grid').innerHTML=posts.slice(10,14).map(function(p,i){{
    return '<div class="grid-card"><a href="'+(p.slug||'#')+'/"><img src="'+(p.image||picUrl(p.slug||'g'+i,400,140))+'" alt="" loading="lazy"></a><div class="grid-card-body"><div class="grid-tag">'+cat(i+3)+'</div><div class="grid-title"><a href="'+(p.slug||'#')+'/">'+p.title+'</a></div><div class="grid-meta">'+fmt(p.date_iso)+'</div></div></div>';
  }}).join('');
}}

fetch('articles.json').then(function(r){{return r.json();}}).then(render).catch(function(){{
  render([{{title:'Training Smarter, Not Harder: A Periodization Guide',slug:'periodization-guide',meta_description:'{s['hero_sub']}',date_iso:new Date().toISOString()}}]);
}});
{pxjs}
</script>
</body>
</html>"""


def sportiqpro_about(s):
    pxjs  = _pexels_js(s)
    about = _about_block(s, s['bg2'], s['brd'], s['text'], s['muted'], s['primary'])
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>About  -  {s['name']}</title>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:{s['bg']};color:{s['text']};font-family:system-ui,sans-serif;line-height:1.7}}
a{{color:{s['primary']};text-decoration:none}}
#nav{{position:sticky;top:0;background:rgba(15,15,18,.97);border-bottom:2px solid {s['primary']};padding:0 20px;height:56px;display:flex;align-items:center;gap:24px;z-index:100}}
.nav-logo{{font-size:18px;font-weight:900;text-transform:uppercase;color:{s['text']}}}
.nav-logo span{{color:{s['primary']}}}
.wrap{{max-width:800px;margin:0 auto;padding:48px 20px}}
h1{{font-size:32px;font-weight:900;margin-bottom:8px}}
.sub{{color:{s['muted']};font-size:14px;margin-bottom:32px}}
h2{{font-size:18px;font-weight:800;margin:32px 0 12px;color:{s['primary']}}}
p{{margin-bottom:16px;color:{s['text']}}}
#foot{{background:#000;border-top:2px solid {s['primary']};padding:24px 20px;text-align:center;font-size:11px;color:{s['muted']}}}
</style>
</head>
<body>
<nav id="nav"><div class="nav-logo"><a href="/" style="color:{s['text']}"><span>Sport</span>IQ Pro</a></div></nav>
<div id="pxl-wrap" style="height:200px;overflow:hidden;position:relative"><img id="pxl-img" style="width:100%;height:100%;object-fit:cover;opacity:0;transition:opacity .8s;display:block" alt=""><div style="position:absolute;inset:0;background:linear-gradient(to right,{s['bg']}dd,transparent)"></div></div>
<div class="wrap">
  <h1>About {s['name']}</h1>
  <div class="sub">{s['tagline']}</div>
  <h2>Our Mission</h2>
  <p>{s['hero_sub']}</p>
  <h2>The Author</h2>
  <p><strong>{s['author']}</strong>  -  {s['author_title']}</p>
  <p>{s['bio1']}</p>
  <p>{s['bio2']}</p>
  <h2>Editorial Standards</h2>
  <p>Every article published on {s['name']} is reviewed against current peer-reviewed research. Claims are cited where possible. Opinion pieces are clearly labeled as such. We don't accept sponsored content or affiliate-influenced editorial.</p>
  <p><a href="/">← Back to {s['name']}</a></p>
</div>
{about}
<footer id="foot">© {s['name']} · <a href="privacy.html">Privacy</a> · <a href="terms.html">Terms</a></footer>
<script>{pxjs}</script>
</body>
</html>"""


# ─────────────────────────────────────────────────────────────────────────────
# THE DATING EDGE   -  Psychology editorial magazine
# ─────────────────────────────────────────────────────────────────────────────
def datingedge_index(s):
    pxjs   = _pexels_js(s)
    about  = _about_block(s, s['bg2'], s['brd'], s['text'], s['muted'], s['primary'])
    seed   = abs(hash(s['id'])) % 1000
    domain = s.get('domain', f"siavashsed.github.io/{s['id']}")
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{s['name']}  -  {s['tagline']}</title>
<meta name="description" content="{s['hero_sub']}">
<link rel="canonical" href="https://{domain}/">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700;800&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
:root{{--bg:{s['bg']};--bg2:{s['bg2']};--surf:{s['surface']};--text:{s['text']};--muted:{s['muted']};--rose:{s['primary']};--brd:{s['brd']}}}
body{{background:var(--bg);color:var(--text);font-family:'Inter',system-ui,sans-serif;line-height:1.7}}
a{{color:inherit;text-decoration:none}}
img{{max-width:100%;display:block}}
h1,h2,h3,.serif{{font-family:'Playfair Display',Georgia,serif}}
/* NAV */
#nav{{position:sticky;top:0;z-index:100;background:rgba(12,8,16,.96);border-bottom:1px solid var(--brd);backdrop-filter:blur(10px)}}
.nav-inner{{max-width:1200px;margin:0 auto;padding:0 24px;height:60px;display:flex;align-items:center;gap:20px}}
.nav-logo{{font-family:'Playfair Display',serif;font-size:22px;font-weight:700;color:var(--text);flex-shrink:0}}
.nav-logo em{{color:var(--rose);font-style:normal}}
.nav-links{{display:flex;gap:2px;flex:1}}
.nav-links a{{font-size:12px;font-weight:500;color:var(--muted);padding:6px 14px;border-radius:20px;letter-spacing:.3px;transition:all .2s}}
.nav-links a:hover{{color:var(--text);background:rgba(244,63,94,.08)}}
/* HERO */
#hero{{max-width:1200px;margin:0 auto;padding:40px 24px 0;display:grid;grid-template-columns:1.6fr 1fr;gap:32px;align-items:center}}
.hero-left{{position:relative}}
.hero-img-wrap{{border-radius:12px;overflow:hidden;height:440px;background:var(--bg2);margin-bottom:24px}}
.hero-img-wrap img{{width:100%;height:100%;object-fit:cover;opacity:0;transition:opacity .8s;display:block}}
.hero-tag{{font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:2px;color:var(--rose);margin-bottom:12px}}
.hero-title{{font-family:'Playfair Display',serif;font-size:clamp(24px,3.5vw,38px);font-weight:700;line-height:1.2;margin-bottom:12px}}
.hero-desc{{font-size:15px;color:var(--muted);line-height:1.6;margin-bottom:18px}}
.hero-btn{{display:inline-block;border:1px solid var(--rose);color:var(--rose);font-size:12px;font-weight:600;letter-spacing:.5px;padding:10px 24px;border-radius:24px;transition:all .2s}}
.hero-btn:hover{{background:var(--rose);color:#fff}}
.hero-right{{display:flex;flex-direction:column;gap:16px}}
.mini-card{{display:flex;gap:12px;align-items:center;background:var(--surf);border-radius:10px;padding:14px;border:1px solid var(--brd);transition:border-color .2s}}
.mini-card:hover{{border-color:var(--rose)}}
.mini-card img{{width:80px;height:60px;object-fit:cover;border-radius:6px;flex-shrink:0}}
.mini-tag{{font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:1px;color:var(--rose);margin-bottom:4px}}
.mini-title{{font-size:13px;font-weight:600;line-height:1.4}}
.mini-meta{{font-size:10px;color:var(--muted);margin-top:4px}}
/* DIVIDER */
.divider{{display:flex;align-items:center;gap:16px;max-width:1200px;margin:40px auto;padding:0 24px}}
.divider-line{{flex:1;height:1px;background:var(--brd)}}
.divider-label{{font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:2px;color:var(--rose)}}
/* GRID */
.article-grid{{max-width:1200px;margin:0 auto;padding:0 24px;display:grid;grid-template-columns:repeat(3,1fr);gap:24px}}
.a-card{{background:var(--surf);border-radius:12px;overflow:hidden;border:1px solid var(--brd);transition:transform .2s,border-color .2s}}
.a-card:hover{{transform:translateY(-2px);border-color:var(--rose)}}
.a-card img{{width:100%;height:180px;object-fit:cover}}
.a-card-body{{padding:16px}}
.a-tag{{font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:1.5px;color:var(--rose);margin-bottom:8px}}
.a-title{{font-family:'Playfair Display',serif;font-size:16px;font-weight:600;line-height:1.35;margin-bottom:8px}}
.a-meta{{font-size:10px;color:var(--muted)}}
/* PULL QUOTE */
.pullquote{{background:linear-gradient(135deg,{s['bg2']} 0%,{s['surface']} 100%);border-left:3px solid var(--rose);max-width:1200px;margin:48px auto;padding:40px 48px;border-radius:0 12px 12px 0}}
.pullquote blockquote{{font-family:'Playfair Display',serif;font-size:22px;font-style:italic;color:var(--text);line-height:1.5;margin-bottom:12px}}
.pullquote cite{{font-size:12px;color:var(--rose);font-weight:600;text-transform:uppercase;letter-spacing:.8px}}
/* NEWSLETTER */
.nl-band{{background:linear-gradient(135deg,{s['surface']} 0%,{s['bg2']} 100%);border-top:1px solid var(--brd);border-bottom:1px solid var(--brd);padding:56px 24px;text-align:center;margin:48px 0}}
.nl-band h2{{font-family:'Playfair Display',serif;font-size:28px;margin-bottom:8px}}
.nl-band p{{color:var(--muted);font-size:14px;margin-bottom:24px;max-width:480px;margin-left:auto;margin-right:auto}}
.nl-row{{display:flex;gap:8px;max-width:420px;margin:0 auto;justify-content:center}}
.nl-row input{{flex:1;padding:11px 16px;background:var(--bg);border:1px solid var(--brd);border-radius:24px;color:var(--text);font-size:13px}}
.nl-row input:focus{{outline:1px solid var(--rose)}}
.nl-row button{{background:var(--rose);color:#fff;border:none;padding:11px 22px;border-radius:24px;font-size:13px;font-weight:600;cursor:pointer}}
/* FOOTER */
#foot{{background:var(--bg);border-top:1px solid var(--brd);padding:40px 24px;margin-top:60px}}
.foot-inner{{max-width:1200px;margin:0 auto;display:flex;flex-wrap:wrap;gap:20px;justify-content:space-between;align-items:center}}
.foot-logo{{font-family:'Playfair Display',serif;font-size:20px;font-weight:700}}
.foot-logo em{{color:var(--rose);font-style:normal}}
.foot-links{{display:flex;gap:16px}}
.foot-links a{{font-size:12px;color:var(--muted)}}
.foot-links a:hover{{color:var(--rose)}}
.foot-copy{{width:100%;text-align:center;font-size:11px;color:var(--muted);padding-top:20px;border-top:1px solid var(--brd)}}
/* RESPONSIVE */
@media(max-width:900px){{#hero{{grid-template-columns:1fr}}.hero-right{{flex-direction:row;flex-wrap:wrap}}.mini-card{{width:calc(50% - 8px)}}.article-grid{{grid-template-columns:repeat(2,1fr)}}.nav-links{{display:none}}.pullquote{{padding:24px 24px 24px 28px}}}}
@media(max-width:600px){{.article-grid{{grid-template-columns:1fr}}.mini-card{{width:100%}}.hero-img-wrap{{height:280px}}.nl-row{{flex-direction:column}}}}
</style>
</head>
<body>

<!-- NAV -->
<nav id="nav">
  <div class="nav-inner">
    <div class="nav-logo">The <em>Dating</em> Edge</div>
    <div class="nav-links">
      <a href="#">Attachment</a>
      <a href="#">Communication</a>
      <a href="#">First Dates</a>
      <a href="#">Psychology</a>
      <a href="#">Breakups</a>
      <a href="about.html">About</a>
    </div>
  </div>
</nav>

<!-- HERO -->
<div id="hero">
  <div class="hero-left">
    <div class="hero-img-wrap"><img id="hero-img" src="" alt=""></div>
    <div class="hero-tag" id="hero-tag">Featured</div>
    <div class="hero-title serif" id="hero-title">Loading…</div>
    <div class="hero-desc" id="hero-desc"></div>
    <a class="hero-btn" id="hero-link" href="#">Read More →</a>
  </div>
  <div class="hero-right" id="mini-list"></div>
</div>

<!-- DIVIDER -->
<div class="divider"><div class="divider-line"></div><div class="divider-label">Latest Articles</div><div class="divider-line"></div></div>

<!-- GRID -->
<div class="article-grid" id="article-grid"></div>

<!-- PULL QUOTE -->
<div class="pullquote">
  <blockquote>"The patterns we repeat in relationships are rarely about the current partner. They're about the map we drew from our earliest attachments  -  and most people never look at the map."</blockquote>
  <cite> -  {s['author']}, {s['author_title']}</cite>
</div>

<!-- NEWSLETTER -->
<div class="nl-band">
  <h2 class="serif">{s['nl_head']}</h2>
  <p>{s['nl_sub']}</p>
  <div class="nl-row">
    <input type="email" placeholder="your@email.com">
    <button>Subscribe</button>
  </div>
</div>

{about}

<!-- FOOTER -->
<footer id="foot">
  <div class="foot-inner">
    <div class="foot-logo">The <em>Dating</em> Edge</div>
    <div class="foot-links">
      <a href="about.html">About</a>
      <a href="privacy.html">Privacy</a>
      <a href="terms.html">Terms</a>
    </div>
    <div class="foot-copy">© {s['name']}. {s['footer_desc']}</div>
  </div>
</footer>

<script>
var CATS=['Attachment','Communication','First Dates','Psychology','Breakups','Attraction'];
function cat(i){{return CATS[i%CATS.length];}}
function fmt(d){{try{{return new Date(d).toLocaleDateString('en-US',{{month:'short',day:'numeric',year:'numeric'}});}}catch(e){{return '';}}}}
function picUrl(slug,w,h){{var seed=Math.abs(slug.split('').reduce(function(a,c){{return a+c.charCodeAt(0);}},0))%1000;return 'https://picsum.photos/seed/de'+seed+'/'+w+'/'+h;}}

function render(posts){{
  if(!posts||!posts.length)return;
  var p0=posts[0];
  document.getElementById('hero-tag').textContent=cat(0);
  document.getElementById('hero-title').textContent=p0.title||'';
  document.getElementById('hero-desc').textContent=p0.meta_description||'';
  document.getElementById('hero-link').href=(p0.slug||'#')+'/';
  var hi=document.getElementById('hero-img');
  hi.onload=function(){{hi.style.opacity='1';}};
  hi.src=p0.image||picUrl(p0.slug||'hero',900,440);

  // Mini cards (posts 1-4)
  document.getElementById('mini-list').innerHTML=posts.slice(1,5).map(function(p,i){{
    return '<div class="mini-card"><a href="'+(p.slug||'#')+'/"><img src="'+(p.image||picUrl(p.slug||'m'+i,160,120))+'" alt="" loading="lazy"></a><div><div class="mini-tag">'+cat(i+1)+'</div><div class="mini-title"><a href="'+(p.slug||'#')+'/">'+p.title+'</a></div><div class="mini-meta">'+fmt(p.date_iso)+'</div></div></div>';
  }}).join('');

  // Article grid (posts 5-13)
  document.getElementById('article-grid').innerHTML=posts.slice(5,14).map(function(p,i){{
    return '<div class="a-card"><a href="'+(p.slug||'#')+'/"><img src="'+(p.image||picUrl(p.slug||'a'+i,400,180))+'" alt="" loading="lazy"></a><div class="a-card-body"><div class="a-tag">'+cat(i+2)+'</div><div class="a-title serif"><a href="'+(p.slug||'#')+'/">'+p.title+'</a></div><div class="a-meta">'+fmt(p.date_iso)+'</div></div></div>';
  }}).join('');
}}

fetch('articles.json').then(function(r){{return r.json();}}).then(render).catch(function(){{
  render([{{title:'Attachment Styles and Why You Keep Dating the Same Person',slug:'attachment-styles',meta_description:'{s['hero_sub']}',date_iso:new Date().toISOString()}}]);
}});
{pxjs}
</script>
</body>
</html>"""


def datingedge_about(s):
    pxjs  = _pexels_js(s)
    about = _about_block(s, s['bg2'], s['brd'], s['text'], s['muted'], s['primary'])
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>About  -  {s['name']}</title>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Inter:wght@400;500&display=swap" rel="stylesheet">
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:{s['bg']};color:{s['text']};font-family:'Inter',system-ui,sans-serif;line-height:1.7}}
a{{color:{s['primary']};text-decoration:none}}
#nav{{position:sticky;top:0;background:rgba(12,8,16,.96);border-bottom:1px solid {s['brd']};padding:0 24px;height:60px;display:flex;align-items:center;z-index:100}}
.nav-logo{{font-family:'Playfair Display',serif;font-size:20px;font-weight:700;color:{s['text']}}}
.nav-logo em{{color:{s['primary']};font-style:normal}}
.wrap{{max-width:760px;margin:0 auto;padding:56px 24px}}
h1{{font-family:'Playfair Display',serif;font-size:36px;font-weight:700;margin-bottom:8px}}
.sub{{color:{s['muted']};margin-bottom:36px}}
h2{{font-family:'Playfair Display',serif;font-size:20px;margin:32px 0 12px;color:{s['primary']}}}
p{{margin-bottom:16px;color:{s['text']}}}
#foot{{background:{s['bg']};border-top:1px solid {s['brd']};padding:24px;text-align:center;font-size:11px;color:{s['muted']}}}
</style>
</head>
<body>
<nav id="nav"><div class="nav-logo"><a href="/" style="color:{s['text']}">The <em>Dating</em> Edge</a></div></nav>
<div id="pxl-wrap" style="height:180px;overflow:hidden;position:relative"><img id="pxl-img" style="width:100%;height:100%;object-fit:cover;opacity:0;transition:opacity .8s;display:block" alt=""><div style="position:absolute;inset:0;background:linear-gradient(to right,{s['bg']}dd,transparent)"></div></div>
<div class="wrap">
  <h1>About The Dating Edge</h1>
  <div class="sub">{s['tagline']}</div>
  <h2>Our Mission</h2>
  <p>{s['hero_sub']}</p>
  <h2>The Author</h2>
  <p><strong>{s['author']}</strong>  -  {s['author_title']}</p>
  <p>{s['bio1']}</p>
  <p>{s['bio2']}</p>
  <h2>Editorial Standards</h2>
  <p>Every article on {s['name']} is grounded in peer-reviewed psychology and relationship research. Opinion pieces are clearly labeled. We do not accept sponsored content that conflicts with our editorial independence.</p>
  <p><a href="/">← Back to {s['name']}</a></p>
</div>
{about}
<footer id="foot">© {s['name']} · <a href="privacy.html">Privacy</a> · <a href="terms.html">Terms</a></footer>
<script>{pxjs}</script>
</body>
</html>"""


# ── Template: pulse ────────────────────────────────────────────────────────────
def pulse_index(s):
    pxjs = _pexels_js(s)
    _topics_map = {
        'tradingtechreview': ['Algo Trading','Backtesting','API Brokers','Python Libs','Data Feeds','Options Tools','Risk Systems','Order Routing','Quant Strategy','Platform Reviews'],
        'carverge':          ['Electric Vehicles','Battery Tech','Fast Charging','EV Reviews','Industry News','Autonomous','Hybrids','Infrastructure','Range Tech','Policy'],
    }
    site_topics = _topics_map.get(s['id'], ['Featured','Analysis','Reviews','News','Guides','Opinion','Interviews','Data','Research','Tools'])
    topics_html = ''.join(f'<span class="ptag">{t}</span>' for t in site_topics)
    _ticker_map = {
        'tradingtechreview': f"{s['category'].upper()} · {s['tagline']} · Platform reviews &amp; API benchmarks · {s['author']} · Algo trading tools, backtesting frameworks, order routing · {s['name']}",
        'carverge':          f"{s['category'].upper()} · {s['tagline']} · Latest EV news &amp; engineering analysis · {s['author']} · Electric vehicles, battery technology, charging infrastructure · {s['name']}",
    }
    ticker_text = _ticker_map.get(s['id'], f"{s['category'].upper()} · {s['tagline']} · {s['author']} · {s['name']}")
    is_tech = s['id'] == 'tradingtechreview'
    term_css = f"""
.term-section{{padding:52px 0;background:{s['surface']};border-top:1px solid {s['brd']};border-bottom:1px solid {s['brd']}}}
.term-inner{{max-width:1200px;margin:0 auto;padding:0 20px;display:grid;grid-template-columns:1fr 1fr;gap:44px;align-items:center}}
.term-info-lbl{{font-size:10px;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:{s['primary']};margin-bottom:12px}}
.term-info-ttl{{font-size:clamp(20px,3vw,30px);font-weight:900;line-height:1.2;margin-bottom:14px;letter-spacing:-.5px;color:{s['text']}}}
.term-info-dsc{{font-size:14px;color:{s['muted']};line-height:1.7;margin-bottom:20px}}
.term-badges{{display:flex;gap:8px;flex-wrap:wrap}}
.term-badge{{font-size:10px;font-weight:700;padding:4px 10px;border:1px solid {s['primary']};border-radius:2px;color:{s['primary']};letter-spacing:.5px}}
.term-win{{background:#0d1117;border:1px solid #30363d;border-radius:8px;overflow:hidden;font-family:'Courier New',Courier,monospace}}
.term-winbar{{background:#161b22;padding:10px 14px;display:flex;align-items:center;gap:6px;border-bottom:1px solid #30363d}}
.term-winbar-dot{{width:12px;height:12px;border-radius:50%}}
.term-winbar-name{{font-size:11px;color:#8b949e;margin-left:6px}}
.term-code{{padding:20px;font-size:12px;line-height:1.85;color:#c9d1d9;overflow-x:auto}}
.t-kw{{color:#ff7b72}}.t-fn{{color:#d2a8ff}}.t-str{{color:#a5d6ff}}.t-nu{{color:#79c0ff}}.t-cm{{color:#8b949e}}
@media(max-width:900px){{.term-inner{{grid-template-columns:1fr}}}}""" if is_tech else ""
    term_section = f"""
<div class="term-section reveal">
  <div class="term-inner">
    <div>
      <div class="term-info-lbl">From the reviews</div>
      <div class="term-info-ttl">Every platform review includes real backtesting code</div>
      <div class="term-info-dsc">We benchmark every tool against live market data using the same Python strategy. No vendor demos, no synthetic results.</div>
      <div class="term-badges">
        <span class="term-badge">Python</span>
        <span class="term-badge">Backtrader</span>
        <span class="term-badge">CCXT</span>
        <span class="term-badge">Alpaca API</span>
        <span class="term-badge">IB Gateway</span>
      </div>
    </div>
    <div class="term-win">
      <div class="term-winbar">
        <div class="term-winbar-dot" style="background:#ff5f56"></div>
        <div class="term-winbar-dot" style="background:#ffbd2e"></div>
        <div class="term-winbar-dot" style="background:#27c93f"></div>
        <span class="term-winbar-name">strategy_benchmark.py</span>
      </div>
      <div class="term-code">
<span class="t-kw">import</span> pandas <span class="t-kw">as</span> pd<br>
<span class="t-kw">from</span> backtesting <span class="t-kw">import</span> <span class="t-fn">Strategy</span>, <span class="t-fn">Backtest</span><br><br>
<span class="t-kw">class</span> <span class="t-fn">MACross</span>(<span class="t-fn">Strategy</span>):<br>
&nbsp;&nbsp;n1, n2 = <span class="t-nu">10</span>, <span class="t-nu">30</span><br><br>
&nbsp;&nbsp;<span class="t-kw">def</span> <span class="t-fn">init</span>(self):<br>
&nbsp;&nbsp;&nbsp;&nbsp;c = self.data.Close<br>
&nbsp;&nbsp;&nbsp;&nbsp;self.ma1 = self.I(c.rolling, self.n1)<br>
&nbsp;&nbsp;&nbsp;&nbsp;self.ma2 = self.I(c.rolling, self.n2)<br><br>
&nbsp;&nbsp;<span class="t-kw">def</span> <span class="t-fn">next</span>(self):<br>
&nbsp;&nbsp;&nbsp;&nbsp;<span class="t-kw">if</span> self.ma1[-<span class="t-nu">1</span>] &gt; self.ma2[-<span class="t-nu">1</span>]:<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.position.close(); self.buy()<br>
&nbsp;&nbsp;&nbsp;&nbsp;<span class="t-cm"># Full code in every platform review</span>
      </div>
    </div>
  </div>
</div>""" if is_tech else ""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{s['name']}  -  {s['tagline']}</title>
<meta name="description" content="{s['hero_sub']}">
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',system-ui,sans-serif;background:{s['bg']};color:{s['text']};font-size:15px;line-height:1.6}}
a{{color:inherit;text-decoration:none}}
.brk{{background:{s['primary']};color:#fff;font-size:11px;font-weight:700;padding:6px 0;display:flex;align-items:center;overflow:hidden}}
.brk-label{{background:rgba(0,0,0,.25);padding:5px 16px;font-size:10px;letter-spacing:2px;text-transform:uppercase;flex-shrink:0;margin-right:14px}}
.brk-ticker{{overflow:hidden;flex:1}}
.brk-ticker span{{display:inline-block;white-space:nowrap;animation:ticker 30s linear infinite}}
@keyframes ticker{{from{{transform:translateX(100vw)}}to{{transform:translateX(-100%)}}}}
.nav{{display:flex;align-items:center;justify-content:space-between;padding:0 32px;height:58px;border-bottom:2px solid {s['primary']};background:{s['bg2']};position:sticky;top:0;z-index:100}}
.nav-left{{display:flex;align-items:center;gap:0;height:100%}}
.nav-logo{{font-size:22px;font-weight:900;letter-spacing:-1px;color:{s['text']};margin-right:28px;flex-shrink:0}}
.nav-logo em{{color:{s['primary']};font-style:normal}}
.nav-links{{display:flex;height:100%}}
.nav-links a{{display:flex;align-items:center;padding:0 13px;font-size:13px;font-weight:600;color:{s['muted']};border-bottom:2px solid transparent;margin-bottom:-2px;transition:all .2s}}
.nav-links a:hover{{color:{s['text']};border-bottom-color:{s['primary']}}}
.nav-date{{font-size:11px;color:{s['muted']};font-weight:500}}
.hero{{display:grid;grid-template-columns:1fr 310px;min-height:500px;border-bottom:1px solid {s['brd']}}}
.hero-main{{position:relative;overflow:hidden;background:{s['bg2']}}}
.hero-main img{{width:100%;height:100%;object-fit:cover;display:block;opacity:0;transition:opacity .8s;position:absolute;inset:0}}
.hero-overlay{{position:absolute;inset:0;background:linear-gradient(to top,{s['bg']}f2 0%,{s['bg']}55 55%,transparent 100%);z-index:1}}
.hero-content{{position:absolute;bottom:0;left:0;right:0;padding:30px;z-index:2}}
.hero-kicker{{display:inline-block;background:{s['primary']};color:#fff;font-size:9px;font-weight:800;letter-spacing:2.5px;text-transform:uppercase;padding:4px 10px;margin-bottom:12px}}
.hero-title{{font-size:clamp(22px,3vw,38px);font-weight:900;line-height:1.12;letter-spacing:-0.5px;margin-bottom:10px;color:{s['text']}}}
.hero-desc{{font-size:14px;color:{s['muted']};line-height:1.65;margin-bottom:12px}}
.hero-meta{{font-size:12px;color:{s['muted']};display:flex;gap:12px;align-items:center}}
.hero-rt{{background:{s['primary']}22;color:{s['primary']};font-size:10px;font-weight:700;padding:3px 8px;border-radius:2px}}
.hero-side{{border-left:1px solid {s['brd']};background:{s['bg2']};display:flex;flex-direction:column}}
.side-hd{{font-size:9px;font-weight:800;letter-spacing:2.5px;text-transform:uppercase;color:{s['primary']};padding:13px 16px;border-bottom:1px solid {s['brd']};flex-shrink:0}}
.side-item{{display:grid;grid-template-columns:76px 1fr;border-bottom:1px solid {s['brd']};cursor:pointer;transition:background .15s}}
.side-item:hover{{background:{s['bg']}}}
.side-item img{{width:76px;height:68px;object-fit:cover;display:block}}
.side-item-ph{{width:76px;height:68px;background:{s['bg']};display:block}}
.side-text{{padding:9px 12px;display:flex;flex-direction:column;justify-content:center}}
.side-item-title{{font-size:12px;font-weight:700;line-height:1.35;color:{s['text']};margin-bottom:3px}}
.side-item-meta{{font-size:10px;color:{s['muted']}}}
.topics{{padding:12px 32px;border-bottom:1px solid {s['brd']};display:flex;gap:8px;align-items:center;overflow-x:auto;scrollbar-width:none;background:{s['bg2']}}}
.topics::-webkit-scrollbar{{display:none}}
.topics-lbl{{font-size:9px;font-weight:800;letter-spacing:2px;text-transform:uppercase;color:{s['muted']};flex-shrink:0;margin-right:4px}}
.ptag{{flex-shrink:0;font-size:11px;font-weight:600;padding:5px 12px;border:1px solid {s['brd']};border-radius:2px;color:{s['muted']};cursor:pointer;transition:all .2s;white-space:nowrap}}
.ptag:hover{{border-color:{s['primary']};color:{s['primary']};background:{s['primary']}0d}}
.wrap{{max-width:1200px;margin:0 auto;padding:0 20px}}
.section-hd{{display:flex;align-items:center;gap:14px;padding:34px 0 18px}}
.section-hd-lbl{{font-size:11px;font-weight:800;letter-spacing:2px;text-transform:uppercase;color:{s['text']}}}
.section-hd-line{{flex:1;height:1px;background:{s['brd']}}}
.card-grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:18px;margin-bottom:32px}}
.card{{background:{s['bg2']};border:1px solid {s['brd']};overflow:hidden;cursor:pointer;transition:border-color .2s,transform .2s;border-radius:3px}}
.card:hover{{border-color:{s['primary']};transform:translateY(-3px)}}
.card-img{{width:100%;height:170px;object-fit:cover;display:block}}
.card-img-ph{{width:100%;height:170px;background:{s['bg']};display:block}}
.card-body{{padding:14px}}
.card-cat{{font-size:9px;font-weight:800;color:{s['primary']};letter-spacing:2px;text-transform:uppercase;margin-bottom:6px}}
.card-title{{font-size:14px;font-weight:800;line-height:1.35;color:{s['text']};margin-bottom:5px}}
.card-desc{{font-size:12px;color:{s['muted']};line-height:1.6}}
.card-foot{{font-size:10px;color:{s['muted']};margin-top:8px;display:flex;justify-content:space-between;align-items:center}}
.card-read{{color:{s['primary']};font-weight:700;font-size:11px}}
.nl-wrap{{background:{s['bg2']};border-top:3px solid {s['primary']};padding:52px 24px;text-align:center}}
.nl-wrap h2{{font-size:clamp(20px,3vw,30px);font-weight:900;letter-spacing:-0.5px;margin-bottom:10px}}
.nl-wrap p{{color:{s['muted']};font-size:15px;margin-bottom:24px;max-width:500px;margin-left:auto;margin-right:auto}}
.nl-row{{display:flex;gap:8px;justify-content:center;max-width:460px;margin:0 auto}}
.nl-input{{flex:1;border:1px solid {s['brd']};background:{s['bg']};color:{s['text']};border-radius:2px;padding:12px 16px;font-size:14px;outline:none;transition:border-color .2s}}
.nl-input:focus{{border-color:{s['primary']}}}
.nl-btn{{background:{s['primary']};color:#fff;border:none;border-radius:2px;padding:12px 24px;font-size:14px;font-weight:800;cursor:pointer;transition:opacity .2s}}
.nl-btn:hover{{opacity:.85}}
.foot{{display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;padding:20px 32px;border-top:1px solid {s['brd']};font-size:12px;color:{s['muted']}}}
.foot-links{{display:flex;gap:18px}}.foot-links a{{color:{s['muted']};transition:color .2s}}.foot-links a:hover{{color:{s['primary']}}}
.reveal{{opacity:0;transform:translateY(20px);transition:opacity .6s,transform .6s}}
.reveal.visible{{opacity:1;transform:none}}
@media(max-width:1100px){{.card-grid{{grid-template-columns:repeat(3,1fr)}}}}
@media(max-width:900px){{.hero{{grid-template-columns:1fr}}.hero-side{{display:none}}.card-grid{{grid-template-columns:1fr 1fr}}}}
@media(max-width:600px){{.card-grid{{grid-template-columns:1fr}}.nav{{padding:0 14px}}.nav-links{{display:none}}.wrap{{padding:0 14px}}.nl-row{{flex-direction:column}}.foot{{flex-direction:column;text-align:center;padding:16px}}}}
{term_css}
</style>
</head>
<body>

<div class="brk">
  <span class="brk-label">Live</span>
  <div class="brk-ticker"><span>{ticker_text}</span></div>
</div>

<nav class="nav">
  <div class="nav-left">
    <div class="nav-logo">{s['name'].split()[0]}<em>{''.join(s['name'].split()[1:])}</em></div>
    <div class="nav-links">
      <a href="./">Home</a>
      <a href="about.html">About</a>
      <a href="privacy.html">Privacy</a>
    </div>
  </div>
  <div class="nav-date" id="nav-date"></div>
</nav>

<div class="hero">
  <div class="hero-main">
    <img id="pxl-img" alt="{s['name']}">
    <div class="hero-overlay"></div>
    <div class="hero-content">
      <span class="hero-kicker">{s['category']}</span>
      <h1 class="hero-title" id="hero-title">{s['tagline']}</h1>
      <p class="hero-desc" id="hero-desc">{s['hero_sub']}</p>
      <div class="hero-meta" id="hero-meta">
        <span>{s['author']}</span>
        <span class="hero-rt">5 min read</span>
      </div>
    </div>
  </div>
  <div class="hero-side">
    <div class="side-hd">Top Stories</div>
    <div id="side-feed"></div>
  </div>
</div>

<div class="topics">
  <span class="topics-lbl">Topics</span>
  {topics_html}
</div>

<div class="wrap">
  <div class="section-hd reveal">
    <span class="section-hd-lbl">Latest Analysis</span>
    <div class="section-hd-line"></div>
  </div>
  <div class="card-grid reveal" id="card-grid"></div>

  <div class="section-hd reveal">
    <span class="section-hd-lbl">More Coverage</span>
    <div class="section-hd-line"></div>
  </div>
  <div class="card-grid reveal" id="more-grid"></div>
</div>

{term_section}

<div class="nl-wrap reveal">
  <h2>{s['nl_head']}</h2>
  <p>{s['nl_sub']}</p>
  <form id="nl-f" onsubmit="nlSub(event)">
    <div class="nl-row">
      <input class="nl-input" type="email" placeholder="your@email.com" required>
      <button class="nl-btn" type="submit">Subscribe</button>
    </div>
  </form>
</div>

<footer class="foot">
  <span>© {s['name']} · {s['footer_desc']}</span>
  <div class="foot-links">
    <a href="./">Home</a><a href="about.html">About</a>
    <a href="privacy.html">Privacy</a><a href="terms.html">Terms</a>
  </div>
</footer>

<script>
document.getElementById('nav-date').textContent=new Date().toLocaleDateString('en-US',{{weekday:'short',month:'short',day:'numeric'}});

async function loadPosts(){{
  try{{
    var r=await fetch('./articles.json');if(!r.ok)throw 0;
    var posts=await r.json();if(!posts||!posts.length)throw 0;
    var h=posts[0];
    if(h.image){{var hi=document.getElementById('pxl-img');if(hi){{hi.onload=function(){{hi.style.opacity='1';}};hi.src=h.image;}}}}
    var ht=document.getElementById('hero-title'),hd=document.getElementById('hero-desc');
    if(ht)ht.innerHTML='<a href="./'+h.slug+'/" style="color:inherit">'+h.title+'</a>';
    if(hd)hd.textContent=(h.meta_description||'').slice(0,160);
    var sf=document.getElementById('side-feed');
    if(sf)sf.innerHTML=posts.slice(1,6).map(function(p){{return '<a href="./'+p.slug+'/" style="display:block"><div class="side-item">'+(p.image?'<img src="'+p.image+'" alt="'+p.title+'">':'<div class="side-item-ph"></div>')+'<div class="side-text"><div class="side-item-title">'+p.title+'</div><div class="side-item-meta">'+(p.date_iso||'')+'</div></div></div></a>';}}).join('');
    function card(p){{return '<a href="./'+p.slug+'/" style="display:block"><div class="card">'+(p.image?'<img class="card-img" src="'+p.image+'" alt="'+p.title+'" loading="lazy">':'<div class="card-img-ph"></div>')+'<div class="card-body"><div class="card-cat">{s['category']}</div><div class="card-title">'+p.title+'</div><div class="card-desc">'+(p.meta_description||'').slice(0,88)+'</div><div class="card-foot"><span>'+(p.date_iso||'')+'</span><span class="card-read">Read →</span></div></div></div></a>';}}
    var cg=document.getElementById('card-grid');if(cg)cg.innerHTML=posts.slice(1,5).map(card).join('');
    var mg=document.getElementById('more-grid');if(mg)mg.innerHTML=posts.slice(5,9).map(card).join('');
  }}catch(e){{
    var cg2=document.getElementById('card-grid');
    if(cg2)cg2.innerHTML='<div class="card"><div class="card-img-ph"></div><div class="card-body"><div class="card-cat">{s['category']}</div><div class="card-title">First articles publishing soon</div><div class="card-desc">Deep {s['category'].lower()} coverage is on its way.</div></div></div>';
  }}
}}
function nlSub(e){{e.preventDefault();document.getElementById('nl-f').innerHTML='<p style="color:{s['primary']};font-weight:700;font-size:15px;padding:12px 0">✓ You\'re on the list.</p>';}}
const obs=new IntersectionObserver(entries=>entries.forEach(en=>{{if(en.isIntersecting){{en.target.classList.add('visible');obs.unobserve(en.target);}}}}),{{threshold:.1}});
document.querySelectorAll('.reveal').forEach(el=>obs.observe(el));
loadPosts();
{pxjs}
</script>
</body></html>"""


def pulse_about(s):
    pxjs = _pexels_js(s)
    story = _story_html(s, 'abt-p')
    ini = ''.join(w[0] for w in s['author'].split() if w)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>About  -  {s['name']}</title>
<meta name="description" content="{s['footer_desc']}">
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',system-ui,sans-serif;background:{s['bg']};color:{s['text']};font-size:15px;line-height:1.75}}
a{{color:{s['primary']};text-decoration:none}}
.nav{{display:flex;align-items:center;justify-content:space-between;padding:16px 28px;border-bottom:3px solid {s['primary']};background:{s['bg2']}}}
.nav-logo{{font-size:22px;font-weight:900;letter-spacing:-0.5px}}
.nav-links{{display:flex;gap:20px}}.nav-links a{{font-size:13px;font-weight:600;color:{s['muted']}}}.nav-links a:hover{{color:{s['primary']}}}
.banner{{background:{s['primary']};padding:48px 28px;text-align:center}}
.banner h1{{font-size:clamp(24px,4vw,44px);font-weight:900;color:#fff;letter-spacing:-1px;margin-bottom:8px}}
.banner p{{color:rgba(255,255,255,.8);font-size:16px}}
.wrap{{max-width:720px;margin:0 auto;padding:48px 20px}}
.avi{{width:72px;height:72px;border-radius:50%;background:{s['primary']};color:#fff;font-size:22px;font-weight:900;display:flex;align-items:center;justify-content:center;margin:0 auto 20px}}
.abt-p{{color:{s['muted']};line-height:1.9;margin-bottom:16px}}
h2{{font-size:18px;font-weight:800;margin:36px 0 12px;color:{s['primary']}}}
.foot{{display:flex;justify-content:space-between;flex-wrap:wrap;gap:10px;padding:20px 28px;border-top:1px solid {s['brd']};font-size:12px;color:{s['muted']}}}
.foot-links{{display:flex;gap:16px}}.foot-links a{{color:{s['muted']}}}
</style>
</head>
<body>
<nav class="nav">
  <div class="nav-logo">{s['name']}</div>
  <div class="nav-links"><a href="./">Home</a><a href="about.html">About</a></div>
</nav>
<div class="banner">
  <h1>About {s['name']}</h1>
  <p>{s['tagline']}</p>
</div>
<div id="pxl-wrap" style="height:180px;overflow:hidden"><img id="pxl-img" style="width:100%;height:100%;object-fit:cover;opacity:0;transition:opacity .8s;display:block" alt=""></div>
<div class="wrap">
  <div class="avi">{ini}</div>
  <h2>{s['author']}</h2>
  <p style="color:{s['primary']};font-weight:700;margin-bottom:16px">{s['author_title']}</p>
  {story}
  <h2>Our Mission</h2>
  <p class="abt-p">{s['hero_sub']}</p>
  <p style="margin-top:28px"><a href="./" style="color:{s['primary']};font-weight:700">← Back to {s['name']}</a></p>
</div>
<footer class="foot">
  <span>© {s['name']} · {s['footer_desc']}</span>
  <div class="foot-links"><a href="privacy.html">Privacy</a><a href="terms.html">Terms</a></div>
</footer>
<script>{pxjs}</script>
</body></html>"""


# ── Template: atlas ────────────────────────────────────────────────────────────
def atlas_index(s):
    pxjs = _pexels_js(s)
    seed = abs(hash(s['id'])) % 1000
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{s['name']}  -  {s['tagline']}</title>
<meta name="description" content="{s['hero_sub']}">
<link href="https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@400;500;600&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:'DM Sans',system-ui,sans-serif;background:{s['bg']};color:{s['text']};font-size:15px;line-height:1.7}}
a{{color:inherit;text-decoration:none}}
/* nav */
.nav{{position:sticky;top:0;z-index:100;display:flex;align-items:center;justify-content:space-between;padding:18px 40px;background:rgba({','.join(str(int(s['bg'].lstrip('#')[i:i+2],16)) for i in (0,2,4))},.96);backdrop-filter:blur(10px);border-bottom:1px solid {s['brd']}}}
.nav-logo{{font-family:'DM Serif Display',serif;font-size:22px;letter-spacing:-0.5px;color:{s['text']}}}
.nav-links{{display:flex;gap:24px}}.nav-links a{{font-size:13px;font-weight:500;color:{s['muted']};transition:color .2s}}.nav-links a:hover{{color:{s['primary']}}}
/* hero full-bleed */
.atlas-hero{{position:relative;height:86vh;min-height:520px;overflow:hidden;background:{s['bg2']}}}
.atlas-hero img{{width:100%;height:100%;object-fit:cover;display:block;opacity:0;transition:opacity 1s}}
.atlas-hero-overlay{{position:absolute;inset:0;background:linear-gradient(165deg,transparent 30%,rgba(0,0,0,.7) 100%)}}
.atlas-hero-content{{position:absolute;bottom:0;left:0;right:0;padding:52px 40px;max-width:760px}}
.hero-tag{{display:inline-block;border:1px solid {s['primary']};color:{s['primary']};font-size:10px;font-weight:600;letter-spacing:2px;text-transform:uppercase;padding:4px 10px;margin-bottom:16px}}
.hero-title{{font-family:'DM Serif Display',serif;font-size:clamp(28px,5vw,54px);line-height:1.1;color:#fff;margin-bottom:14px}}
.hero-sub{{font-size:16px;color:rgba(255,255,255,.8);line-height:1.65;margin-bottom:20px}}
.hero-cta{{display:inline-block;background:{s['primary']};color:#fff;padding:12px 28px;font-size:14px;font-weight:600;border-radius:100px;transition:opacity .2s}}
.hero-cta:hover{{opacity:.85}}
/* editorial grid */
.wrap{{max-width:1160px;margin:0 auto;padding:0 24px}}
.section-label{{font-size:10px;font-weight:700;letter-spacing:3px;text-transform:uppercase;color:{s['primary']};padding:40px 0 18px;border-bottom:2px solid {s['primary']};margin-bottom:28px}}
.feat-grid{{display:grid;grid-template-columns:2fr 1fr;gap:24px;margin-bottom:40px}}
.feat-card{{cursor:pointer;overflow:hidden}}
.feat-card img{{width:100%;height:320px;object-fit:cover;display:block;border-radius:8px;margin-bottom:14px;transition:transform .4s}}
.feat-card:hover img{{transform:scale(1.02)}}
.feat-card-tag{{font-size:10px;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;color:{s['primary']};margin-bottom:8px}}
.feat-card h2{{font-family:'DM Serif Display',serif;font-size:22px;line-height:1.25;color:{s['text']};margin-bottom:8px}}
.feat-card p{{font-size:13px;color:{s['muted']};line-height:1.65}}
.feat-card-date{{font-size:11px;color:{s['muted']};margin-top:10px}}
.stack-card{{display:flex;flex-direction:column;gap:20px}}
.stack-item{{display:grid;grid-template-columns:100px 1fr;gap:12px;cursor:pointer;padding-bottom:20px;border-bottom:1px solid {s['brd']}}}
.stack-item:last-child{{border-bottom:none}}
.stack-item img{{width:100px;height:72px;object-fit:cover;border-radius:6px}}
.stack-item-ph{{width:100px;height:72px;background:{s['bg2']};border-radius:6px;flex-shrink:0}}
.stack-item-title{{font-family:'DM Serif Display',serif;font-size:15px;line-height:1.3;color:{s['text']};margin-bottom:4px}}
.stack-item-date{{font-size:11px;color:{s['muted']}}}
/* more grid */
.more-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:24px;margin-bottom:48px}}
.grid-card{{cursor:pointer}}
.grid-card img{{width:100%;height:200px;object-fit:cover;border-radius:8px;margin-bottom:12px;transition:transform .3s}}
.grid-card:hover img{{transform:scale(1.02)}}
.grid-card-tag{{font-size:10px;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;color:{s['primary']};margin-bottom:6px}}
.grid-card h3{{font-family:'DM Serif Display',serif;font-size:17px;line-height:1.3;color:{s['text']};margin-bottom:6px}}
.grid-card p{{font-size:13px;color:{s['muted']};line-height:1.6}}
/* newsletter */
.nl-section{{background:{s['bg2']};border-radius:16px;padding:52px;margin:0 0 48px;text-align:center;border:1px solid {s['brd']}}}
.nl-section h2{{font-family:'DM Serif Display',serif;font-size:clamp(22px,3vw,34px);margin-bottom:10px}}
.nl-section p{{color:{s['muted']};font-size:15px;margin-bottom:24px}}
.nl-row{{display:flex;gap:10px;justify-content:center;max-width:440px;margin:0 auto}}
.nl-input{{flex:1;border:1px solid {s['brd']};background:{s['bg']};color:{s['text']};border-radius:100px;padding:12px 20px;font-size:14px;outline:none}}
.nl-input:focus{{border-color:{s['primary']}}}
.nl-btn{{background:{s['primary']};color:#fff;border:none;border-radius:100px;padding:12px 24px;font-size:14px;font-weight:600;cursor:pointer;white-space:nowrap}}
/* footer */
.foot{{display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;padding:24px 40px;border-top:1px solid {s['brd']};font-size:12px;color:{s['muted']}}}
.foot-links{{display:flex;gap:20px}}.foot-links a{{color:{s['muted']}}}.foot-links a:hover{{color:{s['primary']}}}
@media(max-width:900px){{.feat-grid{{grid-template-columns:1fr}}.more-grid{{grid-template-columns:1fr 1fr}}.nav{{padding:14px 16px}}}}
@media(max-width:600px){{.more-grid{{grid-template-columns:1fr}}.atlas-hero-content{{padding:32px 16px}}.wrap{{padding:0 16px}}.nl-section{{padding:32px 16px}}.nl-row{{flex-direction:column}}.foot{{flex-direction:column;text-align:center;padding:20px 16px}}}}
</style>
</head>
<body>

<nav class="nav">
  <div class="nav-logo">{s['name']}</div>
  <div class="nav-links">
    <a href="./">Home</a><a href="about.html">About</a><a href="privacy.html">Privacy</a>
  </div>
</nav>

<div class="atlas-hero">
  <img id="pxl-img" alt="{s['name']}">
  <div class="atlas-hero-overlay"></div>
  <div class="atlas-hero-content">
    <span class="hero-tag">{s['category']}</span>
    <h1 class="hero-title" id="hero-title">{s['tagline']}</h1>
    <p class="hero-sub" id="hero-sub">{s['hero_sub']}</p>
    <a class="hero-cta" href="#" id="hero-cta">Read Story →</a>
  </div>
</div>

<div class="wrap">
  <div class="section-label">Featured Stories</div>
  <div class="feat-grid">
    <div class="feat-card" id="feat-main">
      <img src="https://picsum.photos/seed/{seed}a/800/400" alt="" loading="lazy">
      <div class="feat-card-tag">{s['category']}</div>
      <h2>New stories publishing soon</h2>
      <p>{s['hero_sub']}</p>
    </div>
    <div class="stack-card" id="feat-stack"></div>
  </div>

  <div class="section-label">More Stories</div>
  <div class="more-grid" id="more-grid"></div>
</div>

<div class="wrap">
  <div class="nl-section">
    <h2>{s['nl_head']}</h2>
    <p>{s['nl_sub']}</p>
    <form id="nl-f" onsubmit="nlSub(event)">
      <div class="nl-row">
        <input class="nl-input" type="email" placeholder="your@email.com" required>
        <button class="nl-btn" type="submit">Subscribe</button>
      </div>
    </form>
  </div>
</div>

<footer class="foot">
  <span>© {s['name']} · {s['footer_desc']}</span>
  <div class="foot-links">
    <a href="./">Home</a><a href="about.html">About</a>
    <a href="privacy.html">Privacy</a><a href="terms.html">Terms</a>
  </div>
</footer>

<script>
async function loadPosts(){{
  try{{
    var r=await fetch('./articles.json');if(!r.ok)throw 0;
    var posts=await r.json();if(!posts||!posts.length)throw 0;
    var h=posts[0];
    /* hero */
    if(h.image){{var hi=document.getElementById('pxl-img');if(hi){{hi.onload=function(){{hi.style.opacity='1';}};hi.src=h.image;}}}}
    var ht=document.getElementById('hero-title'),hs=document.getElementById('hero-sub'),hc=document.getElementById('hero-cta');
    if(ht)ht.textContent=h.title;
    if(hs)hs.textContent=h.meta_description||'';
    if(hc)hc.href='./'+h.slug+'/';
    /* featured stack */
    var fm=document.getElementById('feat-main');
    if(fm&&posts[0])fm.innerHTML=(posts[0].image?'<img src="'+posts[0].image+'" alt="'+posts[0].title+'" loading="lazy">':'<div style="height:320px;background:{s['bg2']};border-radius:8px;margin-bottom:14px"></div>')+'<div class="feat-card-tag">{s['category']}</div><a href="./'+posts[0].slug+'/"><h2>'+posts[0].title+'</h2></a><p>'+(posts[0].meta_description||'').slice(0,140)+'</p><div class="feat-card-date">'+(posts[0].date_iso||'')+'</div>';
    var fs=document.getElementById('feat-stack');
    if(fs)fs.innerHTML=posts.slice(1,4).map(function(p){{return '<a href="./'+p.slug+'/" style="display:block"><div class="stack-item">'+(p.image?'<img src="'+p.image+'" alt="'+p.title+'" loading="lazy">':'<div class="stack-item-ph"></div>')+'<div><div class="stack-item-title">'+p.title+'</div><div class="stack-item-date">'+(p.date_iso||'')+'</div></div></div></a>';}}).join('');
    /* more grid */
    var mg=document.getElementById('more-grid');
    if(mg)mg.innerHTML=posts.slice(4,7).map(function(p){{return '<a href="./'+p.slug+'/" style="display:block"><div class="grid-card">'+(p.image?'<img src="'+p.image+'" alt="'+p.title+'" loading="lazy">':'<div style="height:200px;background:{s['bg2']};border-radius:8px;margin-bottom:12px"></div>')+'<div class="grid-card-tag">{s['category']}</div><h3>'+p.title+'</h3><p>'+(p.meta_description||'').slice(0,100)+'</p></div></a>';}}).join('');
  }}catch(e){{}}
}}
function nlSub(e){{e.preventDefault();document.getElementById('nl-f').innerHTML='<p style="color:{s['primary']};font-weight:600;font-size:15px;padding:12px 0">✓ You\'re on the list.</p>';}}
loadPosts();
{pxjs}
</script>
</body></html>"""


def atlas_about(s):
    pxjs = _pexels_js(s)
    story = _story_html(s, 'abt-p')
    ini = ''.join(w[0] for w in s['author'].split() if w)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>About  -  {s['name']}</title>
<meta name="description" content="{s['footer_desc']}">
<link href="https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@400;500;600&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:'DM Sans',system-ui,sans-serif;background:{s['bg']};color:{s['text']};font-size:15px;line-height:1.75}}
a{{color:{s['primary']};text-decoration:none}}
.nav{{display:flex;align-items:center;justify-content:space-between;padding:18px 40px;border-bottom:1px solid {s['brd']}}}
.nav-logo{{font-family:'DM Serif Display',serif;font-size:22px;color:{s['text']}}}
.nav-links{{display:flex;gap:20px}}.nav-links a{{font-size:13px;color:{s['muted']};font-weight:500}}
.hero{{height:280px;position:relative;overflow:hidden;background:{s['bg2']}}}
.hero img{{width:100%;height:100%;object-fit:cover;display:block;opacity:0;transition:opacity .8s}}
.hero-ovl{{position:absolute;inset:0;background:linear-gradient(to top,{s['bg']}cc,transparent);display:flex;align-items:flex-end;padding:32px 40px}}
.hero-ovl h1{{font-family:'DM Serif Display',serif;font-size:40px;color:{s['text']}}}
.wrap{{max-width:720px;margin:0 auto;padding:48px 24px}}
.avi{{width:72px;height:72px;border-radius:50%;background:{s['primary']};color:#fff;font-size:22px;font-weight:700;display:flex;align-items:center;justify-content:center;margin-bottom:16px}}
.abt-p{{color:{s['muted']};line-height:1.9;margin-bottom:16px}}
h2{{font-family:'DM Serif Display',serif;font-size:22px;margin:36px 0 12px;color:{s['text']}}}
.foot{{display:flex;justify-content:space-between;flex-wrap:wrap;gap:10px;padding:20px 40px;border-top:1px solid {s['brd']};font-size:12px;color:{s['muted']}}}
.foot-links{{display:flex;gap:16px}}.foot-links a{{color:{s['muted']}}}
@media(max-width:600px){{.nav{{padding:14px 16px}}.hero-ovl{{padding:24px 16px}}.wrap{{padding:36px 16px}}.foot{{flex-direction:column;text-align:center;padding:20px 16px}}}}
</style>
</head>
<body>
<nav class="nav">
  <div class="nav-logo">{s['name']}</div>
  <div class="nav-links"><a href="./">Home</a><a href="about.html">About</a></div>
</nav>
<div class="hero">
  <img id="pxl-img" alt="">
  <div class="hero-ovl"><h1>About {s['name']}</h1></div>
</div>
<div class="wrap">
  <div class="avi">{ini}</div>
  <h2>{s['author']}</h2>
  <p style="color:{s['primary']};font-weight:600;margin-bottom:20px">{s['author_title']}</p>
  {story}
  <h2>Our Mission</h2>
  <p class="abt-p">{s['hero_sub']}</p>
  <p style="margin-top:32px"><a href="./">← Back to {s['name']}</a></p>
</div>
<footer class="foot">
  <span>© {s['name']} · {s['footer_desc']}</span>
  <div class="foot-links"><a href="privacy.html">Privacy</a><a href="terms.html">Terms</a></div>
</footer>
<script>{pxjs}</script>
</body></html>"""


# ── Template: neon ─────────────────────────────────────────────────────────────
def neon_index(s):
    pxjs = _pexels_js(s)
    ico_bolt = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>'
    ico_trend = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>'
    ico_users = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>'
    ico_star = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>'
    ai_topics = ['Strategy','Automation','Analytics','Content AI','Paid Ads','SEO','Social Media','Email','Funnels','CRO']
    topics_html = ''.join(f'<span class="ntag">{t}</span>' for t in ai_topics)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{s['name']}  -  {s['tagline']}</title>
<meta name="description" content="{s['hero_sub']}">
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',system-ui,sans-serif;background:{s['bg']};color:{s['text']};font-size:15px;line-height:1.65}}
a{{color:inherit;text-decoration:none}}
.nav{{display:flex;align-items:center;justify-content:space-between;padding:14px 32px;border-bottom:1px solid {s['brd']};position:sticky;top:0;z-index:100;background:{s['bg']}ee;backdrop-filter:blur(14px)}}
.nav-brand{{display:flex;align-items:center;gap:10px}}
.nav-icon{{width:32px;height:32px;border-radius:8px;background:linear-gradient(135deg,{s['primary']},{s['primary2']});display:flex;align-items:center;justify-content:center;color:#fff;flex-shrink:0;box-shadow:0 0 14px {s['primary']}55}}
.nav-logo{{font-size:18px;font-weight:800;letter-spacing:-0.5px;background:linear-gradient(135deg,{s['primary']},{s['primary2']});-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}}
.nav-links{{display:flex;gap:22px}}.nav-links a{{font-size:13px;color:{s['muted']};font-weight:500;transition:color .2s}}.nav-links a:hover{{color:{s['primary']}}}
.hero{{position:relative;padding:80px 32px 64px;text-align:center;overflow:hidden}}
.hero::before{{content:'';position:absolute;inset:0;background:radial-gradient(ellipse 90% 70% at 50% -10%,{s['primary']}28,transparent 65%);pointer-events:none}}
.hero::after{{content:'';position:absolute;bottom:0;left:0;right:0;height:1px;background:linear-gradient(to right,transparent,{s['brd']},transparent)}}
.hero-badge{{display:inline-flex;align-items:center;gap:6px;border:1px solid {s['primary']}44;background:{s['primary']}11;border-radius:100px;padding:5px 14px;font-size:11px;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:{s['primary']};margin-bottom:24px}}
.hero-dot{{width:6px;height:6px;border-radius:50%;background:{s['primary']};animation:hdot 2s infinite}}
@keyframes hdot{{0%,100%{{box-shadow:0 0 0 0 {s['primary']}55}}50%{{box-shadow:0 0 0 5px transparent}}}}
.hero-title{{font-size:clamp(30px,5.5vw,66px);font-weight:900;letter-spacing:-2.5px;line-height:1.03;margin-bottom:20px;max-width:820px;margin-left:auto;margin-right:auto}}
.hero-title span{{background:linear-gradient(135deg,{s['primary']},{s['primary2']});-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}}
.hero-sub{{font-size:16px;color:{s['muted']};max-width:540px;margin:0 auto 36px;line-height:1.8}}
.hero-actions{{display:flex;align-items:center;justify-content:center;gap:14px;flex-wrap:wrap}}
.hero-btn{{display:inline-block;background:linear-gradient(135deg,{s['primary']},{s['primary2']});color:#fff;border-radius:100px;padding:14px 34px;font-size:15px;font-weight:700;box-shadow:0 0 30px {s['primary']}44;transition:transform .2s,box-shadow .2s}}
.hero-btn:hover{{transform:translateY(-2px);box-shadow:0 0 44px {s['primary']}66}}
.hero-btn2{{display:inline-block;border:1px solid {s['brd']};color:{s['text']};border-radius:100px;padding:13px 28px;font-size:15px;font-weight:600;transition:border-color .2s,color .2s}}
.hero-btn2:hover{{border-color:{s['primary']};color:{s['primary']}}}
.stats{{display:flex;justify-content:center;border-top:1px solid {s['brd']};border-bottom:1px solid {s['brd']}}}
.stat-item{{flex:1;max-width:200px;text-align:center;padding:20px 16px;position:relative}}
.stat-item+.stat-item::before{{content:'';position:absolute;left:0;top:20%;height:60%;width:1px;background:{s['brd']}}}
.stat-num{{font-size:24px;font-weight:900;color:{s['text']};letter-spacing:-1px}}
.stat-label{{font-size:11px;color:{s['muted']};margin-top:2px;text-transform:uppercase;letter-spacing:1px}}
.topics{{padding:18px 32px;border-bottom:1px solid {s['brd']};display:flex;gap:8px;overflow-x:auto;scrollbar-width:none}}
.topics::-webkit-scrollbar{{display:none}}
.ntag{{flex-shrink:0;font-size:12px;font-weight:600;padding:6px 16px;border-radius:100px;border:1px solid {s['brd']};color:{s['muted']};cursor:pointer;transition:all .2s;white-space:nowrap}}
.ntag:hover{{border-color:{s['primary']};color:{s['primary']};background:{s['primary']}11}}
.banner{{height:260px;overflow:hidden;position:relative;margin:0 32px;border-radius:16px;background:{s['bg2']};border:1px solid {s['brd']}}}
.banner img{{width:100%;height:100%;object-fit:cover;opacity:0;transition:opacity .8s;display:block}}
.banner-ovl{{position:absolute;inset:0;background:linear-gradient(135deg,{s['bg']}cc 0%,transparent 60%)}}
.wrap{{max-width:1180px;margin:0 auto;padding:0 24px}}
.s-label{{font-size:11px;font-weight:700;letter-spacing:3px;text-transform:uppercase;color:{s['primary']};padding:44px 0 20px;display:flex;align-items:center;gap:12px}}
.s-label::after{{content:'';flex:1;height:1px;background:linear-gradient(to right,{s['brd']},transparent)}}
.feat-grid{{display:grid;grid-template-columns:1.6fr 1fr;gap:20px;margin-bottom:20px}}
.feat-card{{background:{s['bg2']};border:1px solid {s['brd']};border-radius:16px;overflow:hidden;transition:border-color .25s,transform .25s;display:flex;flex-direction:column}}
.feat-card:hover{{border-color:{s['primary']};transform:translateY(-3px)}}
.feat-card img{{width:100%;height:280px;object-fit:cover;display:block}}
.feat-card-ph{{width:100%;height:280px;background:linear-gradient(135deg,{s['bg']},{s['bg2']});display:block}}
.feat-body{{padding:24px;flex:1;display:flex;flex-direction:column}}
.feat-cat{{font-size:10px;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;color:{s['primary']};margin-bottom:8px}}
.feat-title{{font-size:20px;font-weight:800;line-height:1.3;color:{s['text']};margin-bottom:10px}}
.feat-desc{{font-size:14px;color:{s['muted']};line-height:1.65;flex:1}}
.feat-date{{font-size:11px;color:{s['muted']};margin-top:12px}}
.neon-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:18px;margin-bottom:16px}}
.neon-card{{background:{s['bg2']};border:1px solid {s['brd']};border-radius:14px;overflow:hidden;transition:border-color .25s,transform .25s;display:flex;flex-direction:column}}
.neon-card:hover{{border-color:{s['primary']};transform:translateY(-3px)}}
.neon-card img{{width:100%;height:180px;object-fit:cover;display:block}}
.neon-card-ph{{width:100%;height:180px;background:linear-gradient(135deg,{s['bg']},{s['bg2']});display:block}}
.neon-card-body{{padding:18px;flex:1;display:flex;flex-direction:column}}
.neon-cat{{font-size:10px;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;color:{s['primary']};margin-bottom:6px}}
.neon-title{{font-size:15px;font-weight:700;line-height:1.35;color:{s['text']};margin-bottom:8px;flex:1}}
.neon-desc{{font-size:13px;color:{s['muted']};line-height:1.6}}
.neon-date{{font-size:11px;color:{s['muted']};margin-top:10px}}
.vp-row{{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin:16px 0 48px}}
.vp-card{{background:{s['bg2']};border:1px solid {s['brd']};border-radius:14px;padding:24px;text-align:center;transition:border-color .25s}}
.vp-card:hover{{border-color:{s['primary']}44}}
.vp-icon{{width:44px;height:44px;border-radius:12px;background:{s['primary']}1a;display:flex;align-items:center;justify-content:center;margin:0 auto 12px;color:{s['primary']}}}
.vp-title{{font-size:15px;font-weight:700;margin-bottom:6px}}
.vp-desc{{font-size:13px;color:{s['muted']};line-height:1.6}}
.nl-wrap{{margin:48px 0;background:linear-gradient(135deg,{s['primary']}1a,{s['primary2']}11);border:1px solid {s['primary']}33;border-radius:20px;padding:56px 40px;text-align:center;position:relative;overflow:hidden}}
.nl-glow{{position:absolute;top:-80px;left:50%;transform:translateX(-50%);width:500px;height:300px;background:radial-gradient(ellipse,{s['primary']}22,transparent 70%);pointer-events:none}}
.nl-wrap h2{{font-size:clamp(24px,3vw,34px);font-weight:900;letter-spacing:-0.5px;margin-bottom:10px;position:relative}}
.nl-wrap p{{color:{s['muted']};font-size:15px;margin-bottom:30px;position:relative}}
.nl-row{{display:flex;gap:10px;justify-content:center;max-width:460px;margin:0 auto;position:relative}}
.nl-input{{flex:1;border:1px solid {s['brd']};background:{s['bg']};color:{s['text']};border-radius:100px;padding:14px 22px;font-size:14px;outline:none;transition:border-color .2s}}
.nl-input:focus{{border-color:{s['primary']}}}
.nl-btn{{background:linear-gradient(135deg,{s['primary']},{s['primary2']});color:#fff;border:none;border-radius:100px;padding:14px 28px;font-size:14px;font-weight:700;cursor:pointer;white-space:nowrap;box-shadow:0 0 20px {s['primary']}44}}
.foot{{display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;padding:24px 32px;border-top:1px solid {s['brd']};font-size:12px;color:{s['muted']}}}
.foot-links{{display:flex;gap:20px}}.foot-links a{{color:{s['muted']}}}.foot-links a:hover{{color:{s['primary']}}}
.reveal{{opacity:0;transform:translateY(24px);transition:opacity .6s,transform .6s}}
.reveal.visible{{opacity:1;transform:none}}
@media(max-width:960px){{.feat-grid{{grid-template-columns:1fr}}.neon-grid{{grid-template-columns:1fr 1fr}}.banner{{margin:0 16px}}}}
@media(max-width:600px){{.neon-grid{{grid-template-columns:1fr}}.nav{{padding:12px 16px}}.hero{{padding:56px 16px 44px}}.wrap{{padding:0 16px}}.nl-wrap{{padding:40px 20px}}.nl-row{{flex-direction:column}}.foot{{flex-direction:column;text-align:center;padding:20px 16px}}.topics{{padding:14px 16px}}.vp-row{{grid-template-columns:1fr}}.stats{{flex-wrap:wrap}}}}
</style>
</head>
<body>

<nav class="nav">
  <div class="nav-brand">
    <div class="nav-icon">{ico_bolt}</div>
    <div class="nav-logo">{s['name']}</div>
  </div>
  <div class="nav-links">
    <a href="./">Home</a><a href="about.html">About</a><a href="privacy.html">Privacy</a>
  </div>
</nav>

<div class="hero">
  <div class="hero-badge"><span class="hero-dot"></span>{s['category']}</div>
  <h1 class="hero-title">{s['name'].split()[0]} <span>{''.join(s['name'].split()[1:])}</span></h1>
  <p class="hero-sub">{s['hero_sub']}</p>
  <div class="hero-actions">
    <a class="hero-btn" href="#latest">Start Reading →</a>
    <a class="hero-btn2" href="about.html">About the Author</a>
  </div>
</div>

<div class="stats">
  <div class="stat-item"><div class="stat-num">50+</div><div class="stat-label">Guides</div></div>
  <div class="stat-item"><div class="stat-num">10K+</div><div class="stat-label">Readers</div></div>
  <div class="stat-item"><div class="stat-num">Free</div><div class="stat-label">Always</div></div>
  <div class="stat-item"><div class="stat-num">Weekly</div><div class="stat-label">Updates</div></div>
</div>

<div class="topics">{topics_html}</div>

<div class="banner">
  <img id="pxl-img" alt="{s['name']}">
  <div class="banner-ovl"></div>
</div>

<div class="wrap">
  <div class="s-label reveal" id="latest">Featured</div>
  <div class="feat-grid reveal" id="feat-grid"></div>

  <div class="s-label reveal">Latest Articles</div>
  <div class="neon-grid reveal" id="neon-grid"></div>

  <div class="s-label reveal" id="more-section" style="display:none">More Coverage</div>
  <div class="neon-grid reveal" id="more-grid"></div>
</div>

<div class="wrap reveal">
  <div class="vp-row">
    <div class="vp-card">
      <div class="vp-icon">{ico_trend}</div>
      <div class="vp-title">Expert Analysis</div>
      <div class="vp-desc">Deep dives from AI marketing practitioners, not surface-level takes.</div>
    </div>
    <div class="vp-card">
      <div class="vp-icon">{ico_star}</div>
      <div class="vp-title">Actionable Guides</div>
      <div class="vp-desc">Step-by-step strategies you can implement the same day you read them.</div>
    </div>
    <div class="vp-card">
      <div class="vp-icon">{ico_users}</div>
      <div class="vp-title">Growing Community</div>
      <div class="vp-desc">Join thousands of marketers learning AI-powered growth every week.</div>
    </div>
  </div>
</div>

<div class="wrap">
  <div class="nl-wrap reveal">
    <div class="nl-glow"></div>
    <h2>{s['nl_head']}</h2>
    <p>{s['nl_sub']}</p>
    <form id="nl-f" onsubmit="nlSub(event)">
      <div class="nl-row">
        <input class="nl-input" type="email" placeholder="your@email.com" required>
        <button class="nl-btn" type="submit">Join Free</button>
      </div>
    </form>
  </div>
</div>

<footer class="foot">
  <span>© {s['name']} · {s['footer_desc']}</span>
  <div class="foot-links">
    <a href="./">Home</a><a href="about.html">About</a>
    <a href="privacy.html">Privacy</a><a href="terms.html">Terms</a>
  </div>
</footer>

<script>
async function loadPosts(){{
  try{{
    var r=await fetch('./articles.json');if(!r.ok)throw 0;
    var posts=await r.json();if(!posts||!posts.length)throw 0;
    var fg=document.getElementById('feat-grid');
    if(fg&&posts.length){{
      var fp=posts[0];
      var side2=posts.slice(1,3).map(function(p){{return '<a href="./'+p.slug+'/" style="display:flex;flex:1"><div class="feat-card" style="flex:1">'+(p.image?'<img src="'+p.image+'" alt="'+p.title+'" loading="lazy" style="height:180px">':'<div class="feat-card-ph" style="height:180px"></div>')+'<div class="feat-body"><div class="feat-cat">{s['category']}</div><div class="feat-title" style="font-size:16px">'+p.title+'</div><div class="feat-desc">'+(p.meta_description||'').slice(0,100)+'</div><div class="feat-date">'+(p.date_iso||'')+'</div></div></div></a>';}}).join('');
      fg.innerHTML='<a href="./'+fp.slug+'/" style="display:flex"><div class="feat-card" style="flex:1">'+(fp.image?'<img src="'+fp.image+'" alt="'+fp.title+'" loading="lazy">':'<div class="feat-card-ph"></div>')+'<div class="feat-body"><div class="feat-cat">{s['category']}</div><div class="feat-title" style="font-size:22px;font-weight:900">'+fp.title+'</div><div class="feat-desc">'+(fp.meta_description||'').slice(0,140)+'</div><div class="feat-date">'+(fp.date_iso||'')+'</div></div></div></a><div style="display:flex;flex-direction:column;gap:20px">'+side2+'</div>';
    }}
    function card(p){{return '<a href="./'+p.slug+'/" style="display:flex"><div class="neon-card" style="flex:1">'+(p.image?'<img src="'+p.image+'" alt="'+p.title+'" loading="lazy">':'<div class="neon-card-ph"></div>')+'<div class="neon-card-body"><div class="neon-cat">{s['category']}</div><div class="neon-title">'+p.title+'</div><div class="neon-desc">'+(p.meta_description||'').slice(0,100)+'</div><div class="neon-date">'+(p.date_iso||'')+'</div></div></div></a>';}}
    var ng=document.getElementById('neon-grid');
    if(ng)ng.innerHTML=posts.slice(3,6).map(card).join('');
    var mg=document.getElementById('more-grid');
    var ms=document.getElementById('more-section');
    if(mg&&posts.length>6){{mg.innerHTML=posts.slice(6).map(card).join('');if(ms)ms.style.display='';}}
  }}catch(e){{
    var fg2=document.getElementById('feat-grid');
    if(fg2)fg2.innerHTML='<a href="#" style="display:flex"><div class="feat-card" style="flex:1"><div class="feat-card-ph"></div><div class="feat-body"><div class="feat-cat">{s['category']}</div><div class="feat-title">First articles arriving soon</div><div class="feat-desc">{s['hero_sub']}</div></div></div></a>';
  }}
}}
function nlSub(e){{e.preventDefault();document.getElementById('nl-f').innerHTML='<p style="color:{s['primary']};font-weight:700;font-size:15px;padding:12px 0">✓ You\'re in. Check your inbox.</p>';}}
const obs=new IntersectionObserver(entries=>entries.forEach(en=>{{if(en.isIntersecting){{en.target.classList.add('visible');obs.unobserve(en.target);}}}}),{{threshold:.1}});
document.querySelectorAll('.reveal').forEach(el=>obs.observe(el));
loadPosts();
{pxjs}
</script>
</body></html>"""


def neon_about(s):
    pxjs = _pexels_js(s)
    story = _story_html(s, 'abt-p')
    ini = ''.join(w[0] for w in s['author'].split() if w)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>About  -  {s['name']}</title>
<meta name="description" content="{s['footer_desc']}">
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',system-ui,sans-serif;background:{s['bg']};color:{s['text']};font-size:15px;line-height:1.75}}
a{{color:{s['primary']};text-decoration:none}}
.nav{{display:flex;align-items:center;justify-content:space-between;padding:16px 32px;border-bottom:1px solid {s['brd']};position:sticky;top:0;background:{s['bg']}ee;backdrop-filter:blur(12px);z-index:10}}
.nav-logo{{font-size:20px;font-weight:800;background:linear-gradient(135deg,{s['primary']},{s['primary2']});-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}}
.nav-links{{display:flex;gap:20px}}.nav-links a{{font-size:13px;color:{s['muted']};font-weight:500}}
.hero{{padding:60px 32px;text-align:center;position:relative;overflow:hidden}}
.hero::before{{content:'';position:absolute;inset:0;background:radial-gradient(ellipse 80% 60% at 50% 0%,{s['primary']}22,transparent 70%);pointer-events:none}}
.hero h1{{font-size:clamp(26px,5vw,48px);font-weight:900;letter-spacing:-1.5px;margin-bottom:8px}}
.hero p{{color:{s['muted']};font-size:16px}}
.wrap{{max-width:700px;margin:0 auto;padding:48px 24px}}
.avi{{width:80px;height:80px;border-radius:50%;background:linear-gradient(135deg,{s['primary']},{s['primary2']});color:#fff;font-size:24px;font-weight:900;display:flex;align-items:center;justify-content:center;margin:0 auto 20px}}
.abt-p{{color:{s['muted']};line-height:1.9;margin-bottom:16px}}
h2{{font-size:18px;font-weight:800;margin:36px 0 12px;color:{s['primary']}}}
.foot{{display:flex;justify-content:space-between;flex-wrap:wrap;gap:10px;padding:20px 32px;border-top:1px solid {s['brd']};font-size:12px;color:{s['muted']}}}
.foot-links{{display:flex;gap:16px}}.foot-links a{{color:{s['muted']}}}
</style>
</head>
<body>
<nav class="nav">
  <div class="nav-logo">{s['name']}</div>
  <div class="nav-links"><a href="./">Home</a><a href="about.html">About</a></div>
</nav>
<div class="hero"><h1>About {s['name']}</h1><p>{s['tagline']}</p></div>
<div id="pxl-wrap" style="height:160px;overflow:hidden"><img id="pxl-img" style="width:100%;height:100%;object-fit:cover;opacity:0;transition:opacity .8s;display:block" alt=""></div>
<div class="wrap">
  <div class="avi">{ini}</div>
  <h2 style="text-align:center">{s['author']}</h2>
  <p style="text-align:center;color:{s['primary']};font-weight:600;margin-bottom:28px">{s['author_title']}</p>
  {story}
  <h2>Our Mission</h2>
  <p class="abt-p">{s['hero_sub']}</p>
  <p style="margin-top:28px"><a href="./">← Back to {s['name']}</a></p>
</div>
<footer class="foot">
  <span>© {s['name']} · {s['footer_desc']}</span>
  <div class="foot-links"><a href="privacy.html">Privacy</a><a href="terms.html">Terms</a></div>
</footer>
<script>{pxjs}</script>
</body></html>"""


# ── Template: bloom ────────────────────────────────────────────────────────────
def bloom_index(s):
    pxjs = _pexels_js(s)
    seed = abs(hash(s['id'])) % 1000
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{s['name']}  -  {s['tagline']}</title>
<meta name="description" content="{s['hero_sub']}">
<link href="https://fonts.googleapis.com/css2?family=Lora:wght@400;600;700&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:'Inter',system-ui,sans-serif;background:{s['bg']};color:{s['text']};font-size:15px;line-height:1.7}}
a{{color:inherit;text-decoration:none}}
/* nav */
.nav{{display:flex;align-items:center;justify-content:space-between;padding:20px 48px;border-bottom:1px solid {s['brd']};background:{s['bg']}}}
.nav-logo{{font-family:'Lora',Georgia,serif;font-size:24px;font-weight:700;color:{s['text']};letter-spacing:-0.3px}}
.nav-logo span{{color:{s['primary']}}}
.nav-links{{display:flex;gap:24px}}.nav-links a{{font-size:13px;color:{s['muted']};font-weight:500;transition:color .2s}}.nav-links a:hover{{color:{s['primary']}}}
/* hero */
.hero{{display:grid;grid-template-columns:1fr 1fr;min-height:500px;background:{s['bg2']};border-bottom:1px solid {s['brd']}}}
.hero-img{{overflow:hidden;position:relative}}
.hero-img img{{width:100%;height:100%;object-fit:cover;display:block;opacity:0;transition:opacity .8s;position:absolute;inset:0}}
.hero-img-ph{{width:100%;height:100%;background:linear-gradient(135deg,{s['bg2']},{s['brd']})}}
.hero-content{{padding:56px 48px;display:flex;flex-direction:column;justify-content:center}}
.hero-eyebrow{{font-size:11px;font-weight:600;letter-spacing:3px;text-transform:uppercase;color:{s['primary']};margin-bottom:16px}}
.hero-title{{font-family:'Lora',Georgia,serif;font-size:clamp(24px,3vw,40px);font-weight:700;line-height:1.2;color:{s['text']};margin-bottom:16px}}
.hero-desc{{font-size:15px;color:{s['muted']};line-height:1.8;margin-bottom:24px}}
.hero-cta{{display:inline-block;background:{s['primary']};color:#fff;border-radius:100px;padding:12px 28px;font-size:14px;font-weight:600;align-self:flex-start;transition:background .2s}}
.hero-cta:hover{{background:{s['primary2']}}}
/* article section */
.wrap{{max-width:1120px;margin:0 auto;padding:0 24px}}
.s-label{{font-family:'Lora',Georgia,serif;font-size:22px;font-weight:700;color:{s['text']};padding:40px 0 20px;border-bottom:2px solid {s['primary']};margin-bottom:28px}}
.bloom-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:28px;margin-bottom:48px}}
.bloom-card{{background:{s['bg2']};border-radius:16px;overflow:hidden;border:1px solid {s['brd']};cursor:pointer;transition:box-shadow .25s,transform .25s}}
.bloom-card:hover{{box-shadow:0 8px 32px rgba(0,0,0,.1);transform:translateY(-4px)}}
.bloom-card img{{width:100%;height:200px;object-fit:cover;display:block}}
.bloom-card-ph{{width:100%;height:200px;background:linear-gradient(135deg,{s['bg']},{s['brd']});display:block}}
.bloom-card-body{{padding:20px}}
.bloom-cat{{font-size:10px;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;color:{s['primary']};margin-bottom:8px}}
.bloom-title{{font-family:'Lora',Georgia,serif;font-size:17px;font-weight:700;line-height:1.3;color:{s['text']};margin-bottom:8px}}
.bloom-desc{{font-size:13px;color:{s['muted']};line-height:1.65}}
.bloom-date{{font-size:11px;color:{s['muted']};margin-top:10px}}
/* pull feature */
.pull-feat{{display:grid;grid-template-columns:1fr 1fr;gap:0;background:{s['bg2']};border:1px solid {s['brd']};border-radius:16px;overflow:hidden;margin-bottom:48px}}
.pull-feat img{{width:100%;height:100%;object-fit:cover;min-height:300px}}
.pull-feat-body{{padding:40px;display:flex;flex-direction:column;justify-content:center}}
.pull-feat-eyebrow{{font-size:10px;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:{s['primary']};margin-bottom:12px}}
.pull-feat-title{{font-family:'Lora',Georgia,serif;font-size:26px;font-weight:700;line-height:1.25;color:{s['text']};margin-bottom:14px}}
.pull-feat-desc{{font-size:14px;color:{s['muted']};line-height:1.8;margin-bottom:20px}}
.pull-feat-link{{color:{s['primary']};font-weight:600;font-size:14px}}
/* newsletter */
.nl-wrap{{background:{s['bg2']};border-radius:20px;border:1px solid {s['brd']};padding:52px;text-align:center;margin-bottom:48px}}
.nl-wrap h2{{font-family:'Lora',Georgia,serif;font-size:clamp(22px,3vw,32px);font-weight:700;margin-bottom:10px}}
.nl-wrap p{{color:{s['muted']};font-size:15px;margin-bottom:24px}}
.nl-row{{display:flex;gap:10px;justify-content:center;max-width:440px;margin:0 auto}}
.nl-input{{flex:1;border:1px solid {s['brd']};background:{s['bg']};color:{s['text']};border-radius:100px;padding:13px 20px;font-size:14px;outline:none}}
.nl-input:focus{{border-color:{s['primary']}}}
.nl-btn{{background:{s['primary']};color:#fff;border:none;border-radius:100px;padding:13px 24px;font-size:14px;font-weight:600;cursor:pointer}}
.nl-btn:hover{{background:{s['primary2']}}}
/* footer */
.foot{{display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;padding:24px 48px;border-top:1px solid {s['brd']};font-size:12px;color:{s['muted']}}}
.foot-links{{display:flex;gap:20px}}.foot-links a{{color:{s['muted']}}}.foot-links a:hover{{color:{s['primary']}}}
@media(max-width:900px){{.hero{{grid-template-columns:1fr}}.hero-img{{height:320px;position:relative}}.hero-img img{{position:absolute}}.bloom-grid{{grid-template-columns:1fr 1fr}}.pull-feat{{grid-template-columns:1fr}}.nav{{padding:16px 20px}}}}
@media(max-width:600px){{.bloom-grid{{grid-template-columns:1fr}}.hero-content{{padding:32px 20px}}.wrap{{padding:0 16px}}.nl-wrap{{padding:36px 16px}}.nl-row{{flex-direction:column}}.foot{{flex-direction:column;text-align:center;padding:20px 16px}}}}
</style>
</head>
<body>

<nav class="nav">
  <div class="nav-logo">{s['name'].split()[0]}<span>{''.join(s['name'].split()[1:])}</span></div>
  <div class="nav-links">
    <a href="./">Home</a><a href="about.html">About</a><a href="privacy.html">Privacy</a>
  </div>
</nav>

<div class="hero">
  <div class="hero-img">
    <img id="pxl-img" alt="{s['name']}">
    <div class="hero-img-ph"></div>
  </div>
  <div class="hero-content">
    <div class="hero-eyebrow">{s['category']}</div>
    <h1 class="hero-title" id="hero-title">{s['tagline']}</h1>
    <p class="hero-desc" id="hero-desc">{s['hero_sub']}</p>
    <a class="hero-cta" href="#" id="hero-cta">Read more →</a>
  </div>
</div>

<div class="wrap">
  <div class="s-label">Latest Articles</div>
  <div class="bloom-grid" id="bloom-grid"></div>

  <div id="pull-feat-wrap"></div>

  <div class="s-label">More to Read</div>
  <div class="bloom-grid" id="more-grid"></div>
</div>

<div class="wrap">
  <div class="nl-wrap">
    <h2>{s['nl_head']}</h2>
    <p>{s['nl_sub']}</p>
    <form id="nl-f" onsubmit="nlSub(event)">
      <div class="nl-row">
        <input class="nl-input" type="email" placeholder="your@email.com" required>
        <button class="nl-btn" type="submit">Subscribe</button>
      </div>
    </form>
  </div>
</div>

<footer class="foot">
  <span>© {s['name']} · {s['footer_desc']}</span>
  <div class="foot-links">
    <a href="./">Home</a><a href="about.html">About</a>
    <a href="privacy.html">Privacy</a><a href="terms.html">Terms</a>
  </div>
</footer>

<script>
async function loadPosts(){{
  try{{
    var r=await fetch('./articles.json');if(!r.ok)throw 0;
    var posts=await r.json();if(!posts||!posts.length)throw 0;
    /* hero */
    var h=posts[0];
    if(h.image){{var hi=document.getElementById('pxl-img');if(hi){{hi.onload=function(){{hi.style.opacity='1';}};hi.src=h.image;}}}}
    var ht=document.getElementById('hero-title'),hd=document.getElementById('hero-desc'),hc=document.getElementById('hero-cta');
    if(ht)ht.innerHTML='<a href="./'+h.slug+'/" style="color:inherit">'+h.title+'</a>';
    if(hd)hd.textContent=h.meta_description||'';
    if(hc)hc.href='./'+h.slug+'/';
    /* card fn */
    function card(p){{return '<a href="./'+p.slug+'/" style="display:block"><div class="bloom-card">'+(p.image?'<img src="'+p.image+'" alt="'+p.title+'" loading="lazy">':'<div class="bloom-card-ph"></div>')+'<div class="bloom-card-body"><div class="bloom-cat">{s['category']}</div><div class="bloom-title">'+p.title+'</div><div class="bloom-desc">'+(p.meta_description||'').slice(0,110)+'</div><div class="bloom-date">'+(p.date_iso||'')+'</div></div></div></a>';}}
    var bg=document.getElementById('bloom-grid');if(bg)bg.innerHTML=posts.slice(1,4).map(card).join('');
    /* pull feature */
    if(posts[4]){{
      var pf=document.getElementById('pull-feat-wrap');
      if(pf)pf.innerHTML='<a href="./'+posts[4].slug+'/" style="display:block"><div class="pull-feat">'+(posts[4].image?'<img src="'+posts[4].image+'" alt="'+posts[4].title+'" loading="lazy">':'')+'<div class="pull-feat-body"><div class="pull-feat-eyebrow">{s['category']}</div><div class="pull-feat-title">'+posts[4].title+'</div><div class="pull-feat-desc">'+(posts[4].meta_description||'').slice(0,160)+'</div><span class="pull-feat-link">Read full article →</span></div></div></a>';
    }}
    var mg=document.getElementById('more-grid');if(mg)mg.innerHTML=posts.slice(5,8).map(card).join('');
  }}catch(e){{
    var bg2=document.getElementById('bloom-grid');
    if(bg2)bg2.innerHTML='<div class="bloom-card"><div class="bloom-card-ph"></div><div class="bloom-card-body"><div class="bloom-cat">{s['category']}</div><div class="bloom-title">First articles coming soon</div><div class="bloom-desc">{s['hero_sub']}</div></div></div>';
  }}
}}
function nlSub(e){{e.preventDefault();document.getElementById('nl-f').innerHTML='<p style="color:{s['primary']};font-weight:600;font-size:15px;padding:12px 0">✓ Welcome to the community!</p>';}}
loadPosts();
{pxjs}
</script>
</body></html>"""


def bloom_about(s):
    pxjs = _pexels_js(s)
    story = _story_html(s, 'abt-p')
    ini = ''.join(w[0] for w in s['author'].split() if w)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>About  -  {s['name']}</title>
<meta name="description" content="{s['footer_desc']}">
<link href="https://fonts.googleapis.com/css2?family=Lora:wght@400;600;700&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:'Inter',system-ui,sans-serif;background:{s['bg']};color:{s['text']};font-size:15px;line-height:1.75}}
a{{color:{s['primary']};text-decoration:none}}
.nav{{display:flex;align-items:center;justify-content:space-between;padding:20px 48px;border-bottom:1px solid {s['brd']}}}
.nav-logo{{font-family:'Lora',Georgia,serif;font-size:22px;font-weight:700;color:{s['text']}}}
.nav-links{{display:flex;gap:20px}}.nav-links a{{font-size:13px;color:{s['muted']};font-weight:500}}
.banner{{background:{s['bg2']};border-bottom:1px solid {s['brd']};padding:52px 48px;text-align:center}}
.banner h1{{font-family:'Lora',Georgia,serif;font-size:clamp(26px,5vw,48px);font-weight:700;color:{s['text']};margin-bottom:8px}}
.banner p{{color:{s['muted']};font-size:16px}}
.pxl{{height:200px;overflow:hidden}}.pxl img{{width:100%;height:100%;object-fit:cover;opacity:0;transition:opacity .8s;display:block}}
.wrap{{max-width:700px;margin:0 auto;padding:52px 24px}}
.avi{{width:80px;height:80px;border-radius:50%;background:{s['primary']};color:#fff;font-size:24px;font-weight:700;display:flex;align-items:center;justify-content:center;margin:0 auto 20px}}
.abt-p{{color:{s['muted']};line-height:1.9;margin-bottom:16px}}
h2{{font-family:'Lora',Georgia,serif;font-size:22px;font-weight:700;margin:36px 0 12px;color:{s['text']}}}
.foot{{display:flex;justify-content:space-between;flex-wrap:wrap;gap:10px;padding:20px 48px;border-top:1px solid {s['brd']};font-size:12px;color:{s['muted']}}}
.foot-links{{display:flex;gap:16px}}.foot-links a{{color:{s['muted']}}}
@media(max-width:600px){{.nav,.foot{{padding:16px 20px;flex-direction:column;text-align:center}}.banner{{padding:36px 20px}}.wrap{{padding:36px 16px}}}}
</style>
</head>
<body>
<nav class="nav">
  <div class="nav-logo">{s['name']}</div>
  <div class="nav-links"><a href="./">Home</a><a href="about.html">About</a></div>
</nav>
<div class="banner">
  <h1>About {s['name']}</h1>
  <p>{s['tagline']}</p>
</div>
<div class="pxl"><img id="pxl-img" alt=""></div>
<div class="wrap">
  <div class="avi">{ini}</div>
  <h2 style="text-align:center">{s['author']}</h2>
  <p style="text-align:center;color:{s['primary']};font-weight:600;margin-bottom:28px">{s['author_title']}</p>
  {story}
  <h2>Our Mission</h2>
  <p class="abt-p">{s['hero_sub']}</p>
  <p style="margin-top:32px"><a href="./">← Back to {s['name']}</a></p>
</div>
<footer class="foot">
  <span>© {s['name']} · {s['footer_desc']}</span>
  <div class="foot-links"><a href="privacy.html">Privacy</a><a href="terms.html">Terms</a></div>
</footer>
<script>{pxjs}</script>
</body></html>"""


# ── Template: slate ────────────────────────────────────────────────────────────
def slate_index(s):
    pxjs = _pexels_js(s)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{s['name']}: {s['tagline']}</title>
<meta name="description" content="{s['hero_sub']}">
<link href="https://fonts.googleapis.com/css2?family=Libre+Baskerville:wght@400;700&family=Source+Sans+3:wght@400;500;600&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:'Source Sans 3',system-ui,sans-serif;background:#ffffff;color:{s['text']};font-size:16px;line-height:1.7}}
a{{color:inherit;text-decoration:none}}
/* top bar */
.topbar{{background:#ffffff;border-bottom:1px solid {s['brd']};padding:8px 0}}
.topbar-inner{{max-width:1200px;margin:0 auto;padding:0 28px;display:flex;align-items:center;justify-content:space-between}}
.topbar-date{{font-size:11px;color:{s['muted']}}}
.topbar-links{{display:flex;gap:20px}}.topbar-links a{{font-size:12px;color:{s['muted']};font-weight:500;transition:color .2s}}.topbar-links a:hover{{color:{s['primary']}}}
/* masthead */
.masthead{{text-align:center;padding:32px 24px 24px;border-bottom:3px solid {s['text']}}}
.site-title{{font-family:'Libre Baskerville',Georgia,serif;font-size:clamp(32px,6vw,64px);font-weight:700;letter-spacing:-2px;color:{s['text']};line-height:1}}
.site-tagline{{font-size:14px;color:{s['muted']};margin-top:10px;font-style:italic;letter-spacing:.3px}}
/* nav */
.site-nav{{display:flex;justify-content:center;gap:32px;padding:12px 24px;border-bottom:1px solid {s['brd']};background:#fafafa}}
.site-nav a{{font-size:12px;font-weight:700;color:{s['muted']};text-transform:uppercase;letter-spacing:1.5px;transition:color .2s}}.site-nav a:hover{{color:{s['primary']}}}
/* main layout: hero left, articles right */
.main-wrap{{max-width:1200px;margin:36px auto 0;padding:0 28px;display:grid;grid-template-columns:1fr 340px;gap:40px;border-bottom:1px solid {s['brd']};padding-bottom:40px}}
/* hero - left */
.feat-label{{font-size:10px;font-weight:700;letter-spacing:2.5px;text-transform:uppercase;color:{s['primary']};margin-bottom:10px}}
.feat-img{{width:100%;height:340px;object-fit:cover;display:block;margin-bottom:18px;background:{s['bg2']}}}
.feat-title{{font-family:'Libre Baskerville',Georgia,serif;font-size:clamp(22px,2.8vw,34px);font-weight:700;line-height:1.2;color:{s['text']};margin-bottom:12px}}
.feat-title a{{color:inherit}}.feat-title a:hover{{color:{s['primary']}}}
.feat-body{{font-size:15px;color:{s['muted']};line-height:1.85;margin-bottom:14px}}
.feat-byline{{font-size:12px;color:{s['muted']};padding-top:12px;border-top:1px solid {s['brd']}}}
/* article list - right column */
.art-list-hd{{font-size:10px;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:{s['text']};padding-bottom:10px;border-bottom:2px solid {s['text']};margin-bottom:0}}
.art-list-item{{display:grid;grid-template-columns:88px 1fr;gap:12px;padding:14px 0;border-bottom:1px solid {s['brd']};cursor:pointer;transition:background .1s}}
.art-list-item:hover .ali-title{{color:{s['primary']}}}
.ali-img{{width:88px;height:64px;object-fit:cover;display:block;background:{s['bg2']}}}
.ali-body{{display:flex;flex-direction:column;justify-content:center}}
.ali-cat{{font-size:9px;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;color:{s['primary']};margin-bottom:4px}}
.ali-title{{font-family:'Libre Baskerville',Georgia,serif;font-size:13px;font-weight:700;line-height:1.3;color:{s['text']}}}
.ali-date{{font-size:10px;color:{s['muted']};margin-top:4px}}
/* more grid */
.more-section{{max-width:1200px;margin:0 auto;padding:36px 28px 0}}
.more-hd{{font-size:10px;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:{s['text']};padding-bottom:10px;border-bottom:2px solid {s['text']};margin-bottom:24px}}
.more-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:24px;margin-bottom:48px}}
.more-card{{cursor:pointer}}
.more-card img{{width:100%;height:170px;object-fit:cover;display:block;margin-bottom:12px;background:{s['bg2']}}}
.more-card-ph{{width:100%;height:170px;background:{s['bg2']};display:block;margin-bottom:12px}}
.more-cat{{font-size:9px;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;color:{s['primary']};margin-bottom:6px}}
.more-title{{font-family:'Libre Baskerville',Georgia,serif;font-size:16px;font-weight:700;line-height:1.3;color:{s['text']};margin-bottom:6px}}
.more-title:hover{{color:{s['primary']}}}
.more-desc{{font-size:13px;color:{s['muted']};line-height:1.6}}
/* newsletter */
.nl-section{{background:#fafafa;border-top:1px solid {s['brd']};border-bottom:1px solid {s['brd']};padding:52px 24px;text-align:center}}
.nl-section h2{{font-family:'Libre Baskerville',Georgia,serif;font-size:clamp(20px,3vw,30px);font-weight:700;margin-bottom:10px;color:{s['text']}}}
.nl-section p{{color:{s['muted']};font-size:15px;margin-bottom:24px;max-width:480px;margin-left:auto;margin-right:auto}}
.nl-row{{display:flex;gap:0;justify-content:center;max-width:420px;margin:0 auto;border:1px solid {s['brd']}}}
.nl-input{{flex:1;border:none;background:#fff;color:{s['text']};padding:12px 16px;font-size:14px;outline:none}}
.nl-btn{{background:{s['primary']};color:#fff;border:none;padding:12px 22px;font-size:14px;font-weight:700;cursor:pointer;white-space:nowrap;transition:background .2s}}
.nl-btn:hover{{background:{s['primary2']}}}
/* footer */
.foot{{max-width:1200px;margin:0 auto;padding:20px 28px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;font-size:12px;color:{s['muted']}}}
.foot-links{{display:flex;gap:20px}}.foot-links a{{color:{s['muted']}}}.foot-links a:hover{{color:{s['primary']}}}
@media(max-width:900px){{.main-wrap{{grid-template-columns:1fr}}.more-grid{{grid-template-columns:1fr 1fr}}}}
@media(max-width:600px){{.more-grid{{grid-template-columns:1fr}}.site-nav{{flex-wrap:wrap;gap:10px}}.nl-row{{flex-direction:column;border:none;gap:8px}}.nl-input{{border:1px solid {s['brd']}}}.foot{{flex-direction:column;text-align:center}}}}
</style>
</head>
<body>

<div class="topbar">
  <div class="topbar-inner">
    <span class="topbar-date" id="topbar-date"></span>
    <div class="topbar-links">
      <a href="./">Home</a><a href="about.html">About</a><a href="privacy.html">Privacy</a>
    </div>
  </div>
</div>

<div class="masthead">
  <div class="site-title">{s['name']}</div>
  <div class="site-tagline">{s['tagline']}</div>
</div>

<nav class="site-nav">
  <a href="./">{s['category']}</a>
  <a href="about.html">About</a>
  <a href="privacy.html">Policy</a>
</nav>

<div class="main-wrap">
  <!-- Featured article: LEFT -->
  <div class="feat-col">
    <div class="feat-label">{s['category']}</div>
    <img id="pxl-img" class="feat-img" alt="{s['name']}" style="opacity:0;transition:opacity .8s">
    <h1 class="feat-title" id="feat-title"><a href="#">{s['tagline']}</a></h1>
    <p class="feat-body" id="feat-desc">{s['hero_sub']}</p>
    <div class="feat-byline" id="feat-byline">By {s['author']} · {s['author_title']}</div>
  </div>
  <!-- Article list: RIGHT -->
  <div class="art-col">
    <div class="art-list-hd">Latest Articles</div>
    <div id="art-list"></div>
  </div>
</div>

<div class="more-section">
  <div class="more-hd">More Coverage</div>
  <div class="more-grid" id="more-grid"></div>
</div>

<div class="nl-section">
  <h2>{s['nl_head']}</h2>
  <p>{s['nl_sub']}</p>
  <form id="nl-f" onsubmit="nlSub(event)">
    <div class="nl-row">
      <input class="nl-input" type="email" placeholder="your@email.com" required>
      <button class="nl-btn" type="submit">Subscribe</button>
    </div>
  </form>
</div>

<footer class="foot">
  <span>© {s['name']} · {s['footer_desc']}</span>
  <div class="foot-links">
    <a href="./">Home</a><a href="about.html">About</a>
    <a href="privacy.html">Privacy</a><a href="terms.html">Terms</a>
  </div>
</footer>

<script>
document.getElementById('topbar-date').textContent=new Date().toLocaleDateString('en-US',{{weekday:'long',month:'long',day:'numeric'}});

async function loadPosts(){{
  try{{
    var r=await fetch('./articles.json');if(!r.ok)throw 0;
    var posts=await r.json();if(!posts||!posts.length)throw 0;
    var h=posts[0];
    /* featured */
    if(h.image){{var hi=document.getElementById('pxl-img');if(hi){{hi.onload=function(){{hi.style.opacity='1';}};hi.src=h.image;}}}}
    var ft=document.getElementById('feat-title'),fd=document.getElementById('feat-desc'),fb=document.getElementById('feat-byline');
    if(ft)ft.innerHTML='<a href="./'+h.slug+'/" style="color:inherit">'+h.title+'</a>';
    if(fd)fd.textContent=h.meta_description||'';
    if(fb)fb.textContent='By '+(h.author||'{s['author']}')+(h.date_iso?' · '+h.date_iso:'');
    /* article list - right column, posts 1-5 */
    var al=document.getElementById('art-list');
    if(al)al.innerHTML=posts.slice(1,6).map(function(p){{
      return '<a href="./'+p.slug+'/" style="display:block"><div class="art-list-item">'+
        (p.image?'<img class="ali-img" src="'+p.image+'" alt="'+p.title+'" loading="lazy">':'<div class="ali-img"></div>')+
        '<div class="ali-body"><div class="ali-cat">{s['category']}</div><div class="ali-title">'+p.title+'</div><div class="ali-date">'+(p.date_iso||'')+'</div></div></div></a>';
    }}).join('');
    /* more grid - posts 6+ */
    var mg=document.getElementById('more-grid');
    if(mg)mg.innerHTML=posts.slice(6,9).map(function(p){{
      return '<a href="./'+p.slug+'/" style="display:block"><div class="more-card">'+
        (p.image?'<img src="'+p.image+'" alt="'+p.title+'" loading="lazy">':'<div class="more-card-ph"></div>')+
        '<div class="more-cat">{s['category']}</div><div class="more-title">'+p.title+'</div><div class="more-desc">'+(p.meta_description||'').slice(0,120)+'</div></div></a>';
    }}).join('');
    if(!posts[6])document.querySelector('.more-section').style.display='none';
  }}catch(e){{
    var al2=document.getElementById('art-list');
    if(al2)al2.innerHTML='<div class="art-list-item"><div class="ali-img"></div><div class="ali-body"><div class="ali-cat">{s['category']}</div><div class="ali-title">First articles arriving soon</div></div></div>';
  }}
}}
function nlSub(e){{e.preventDefault();document.getElementById('nl-f').innerHTML='<p style="color:{s['primary']};font-weight:700;font-size:15px;padding:12px 0">Subscribed. Welcome.</p>';}}
loadPosts();
{pxjs}
</script>
</body></html>"""


def slate_about(s):
    pxjs = _pexels_js(s)
    story = _story_html(s, 'abt-p')
    ini = ''.join(w[0] for w in s['author'].split() if w)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>About: {s['name']}</title>
<meta name="description" content="{s['footer_desc']}">
<link href="https://fonts.googleapis.com/css2?family=Libre+Baskerville:wght@400;700&family=Source+Sans+3:wght@400;500;600&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:'Source Sans 3',system-ui,sans-serif;background:{s['bg']};color:{s['text']};font-size:16px;line-height:1.75}}
a{{color:{s['primary']};text-decoration:none}}
.site-header{{text-align:center;padding:24px;border-bottom:3px double {s['brd']};background:{s['bg2']}}}
.site-title{{font-family:'Libre Baskerville',Georgia,serif;font-size:28px;font-weight:700;color:{s['text']}}}
.nav{{display:flex;justify-content:center;gap:24px;padding:12px 24px;border-bottom:1px solid {s['brd']}}}
.nav a{{font-size:13px;font-weight:600;color:{s['muted']};text-transform:uppercase;letter-spacing:1px}}
.hero{{height:220px;overflow:hidden;position:relative;background:{s['bg2']}}}
.hero img{{width:100%;height:100%;object-fit:cover;opacity:0;transition:opacity .8s;display:block}}
.hero-label{{position:absolute;bottom:20px;left:24px;font-family:'Libre Baskerville',Georgia,serif;font-size:28px;font-weight:700;color:{s['text']}}}
.wrap{{max-width:700px;margin:0 auto;padding:52px 24px}}
.avi{{width:72px;height:72px;border-radius:50%;background:{s['primary']};color:#fff;font-size:20px;font-weight:700;display:flex;align-items:center;justify-content:center;margin-bottom:16px}}
.abt-p{{color:{s['muted']};line-height:1.9;margin-bottom:16px}}
h2{{font-family:'Libre Baskerville',Georgia,serif;font-size:22px;font-weight:700;margin:36px 0 12px;color:{s['text']};border-bottom:1px solid {s['brd']};padding-bottom:8px}}
.foot{{display:flex;justify-content:space-between;flex-wrap:wrap;gap:10px;padding:20px 24px;border-top:1px solid {s['brd']};font-size:12px;color:{s['muted']}}}
.foot-links{{display:flex;gap:16px}}.foot-links a{{color:{s['muted']}}}
</style>
</head>
<body>
<div class="site-header"><div class="site-title">{s['name']}</div></div>
<nav class="nav"><a href="./">Home</a><a href="about.html">About</a><a href="privacy.html">Privacy</a></nav>
<div class="hero">
  <img id="pxl-img" alt="">
  <div class="hero-label">About Us</div>
</div>
<div class="wrap">
  <div class="avi">{ini}</div>
  <h2>{s['author']}</h2>
  <p style="color:{s['primary']};font-weight:600;margin-bottom:20px">{s['author_title']}</p>
  {story}
  <h2>Our Mission</h2>
  <p class="abt-p">{s['hero_sub']}</p>
  <p style="margin-top:32px"><a href="./">← Back to {s['name']}</a></p>
</div>
<footer class="foot">
  <span>© {s['name']} · {s['footer_desc']}</span>
  <div class="foot-links"><a href="privacy.html">Privacy</a><a href="terms.html">Terms</a></div>
</footer>
<script>{pxjs}</script>
</body></html>"""


# ── Dispatch ───────────────────────────────────────────────────────────────────
GENERATORS = {
    "terminal":   (terminal_index,    terminal_about),
    "stack":      (stack_index,       stack_about),
    "grid":       (grid_index,        grid_about),
    "leaf":       (leaf_index,        leaf_about),
    "forge":      (forge_index,       forge_about),
    "sportiqpro": (sportiqpro_index,  sportiqpro_about),
    "datingedge": (datingedge_index,  datingedge_about),
    "pulse":      (pulse_index,       pulse_about),
    "atlas":      (atlas_index,       atlas_about),
    "neon":       (neon_index,        neon_about),
    "bloom":      (bloom_index,       bloom_about),
    "slate":      (slate_index,       slate_about),
}

def generate(site):
    """Index is the homepage template (the single source of truth for site chrome).
    The about page is built by gen_about(), wrapped in that same homepage shell."""
    s   = dict(site)
    _tmpl = BASE / "templates" / f"{s['id']}-index.html"
    if not _tmpl.exists():
        raise FileNotFoundError(f"Template not found: {_tmpl}")
    layout_shell.validate_markers(s['id'])
    index_html = layout_shell.clean(_tmpl.read_text(encoding="utf-8"))
    about_html = gen_about(s)
    return index_html, about_html


# ── Save locally ───────────────────────────────────────────────────────────────
_EXTRA_TITLES = {"resources": "Resources & Tools", "objections": "Honest Answers",
                 "tools": "Tools", "guides": "Guides", "recaps": "Recaps"}


def extra_pages(s):
    """Bespoke extra pages: about-bodies/<id>-<name>.html becomes <name>.html on the
    site, wrapped in that site's homepage shell."""
    out = []
    d = BASE / "about-bodies"
    if not d.exists():
        return out
    prefix = f"{s['id']}-"
    for f in sorted(d.glob(f"{prefix}*.html")):
        name = f.name[len(prefix):-5]
        title = _EXTRA_TITLES.get(name, name.replace("-", " ").title())
        html = layout_shell.wrap_page(
            s["id"], title=f"{title} - {s['name']}",
            description=f"{title} for {s['name']}.",
            body_html=f.read_text(encoding="utf-8"), depth=0,
        )
        out.append((f"{name}.html", html))
    return out


def save_local(only=None, sites_filter=None):
    filt = set(sites_filter) if sites_filter else ({only} if only else None)
    OUT.mkdir(exist_ok=True)
    for s in SITES:
        if filt and s["id"] not in filt:
            continue
        idx, abt = generate(s)
        d = OUT / s["id"]
        d.mkdir(exist_ok=True)
        (d / "index.html").write_text(_meta_inject(idx, s), encoding="utf-8")
        (d / "about.html").write_text(_meta_inject(abt, s), encoding="utf-8")
        (d / "404.html").write_text(_meta_inject(gen_404(s), s), encoding="utf-8")
        (d / "privacy.html").write_text(_meta_inject(gen_privacy(s), s), encoding="utf-8")
        (d / "terms.html").write_text(_meta_inject(gen_terms(s), s), encoding="utf-8")
        (d / "sms.html").write_text(_meta_inject(gen_sms(s), s), encoding="utf-8")
        (d / "meta-policy.html").write_text(_meta_inject(gen_meta_policy(s), s), encoding="utf-8")
        # Write as articles/index.html so the URL works at both /articles and
        # /articles/ - GitHub Pages 404s the trailing-slash form on bare *.html.
        (d / "articles").mkdir(parents=True, exist_ok=True)
        (d / "articles" / "index.html").write_text(_meta_inject(gen_articles_index(s), s), encoding="utf-8")
        for fn, html in extra_pages(s):
            (d / fn).write_text(_meta_inject(html, s), encoding="utf-8")
        (d / ".nojekyll").write_text("", encoding="utf-8")
        print(f"  ok {s['id']}")
    print(f"\nSaved to {OUT}/")


# ── Push to GitHub ─────────────────────────────────────────────────────────────
def gh_delete(token, repo, path, message="Remove file"):
    url  = f"https://api.github.com/repos/{repo}/contents/{path}"
    hdrs = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}
    existing = requests.get(url, headers=hdrs, timeout=10)
    if existing.status_code == 200:
        sha = existing.json().get("sha", "")
        requests.delete(url, headers=hdrs, json={"message": message, "sha": sha}, timeout=10)


def gh_put(token, repo, path, content, message="Update site template"):
    url  = f"https://api.github.com/repos/{repo}/contents/{path}"
    hdrs = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}
    existing = requests.get(url, headers=hdrs, timeout=10)
    payload  = {
        "message": message,
        "content": base64.b64encode(content.encode()).decode(),
    }
    if existing.status_code == 200:
        payload["sha"] = existing.json()["sha"]
    r = requests.put(url, headers=hdrs, json=payload, timeout=20)
    return r.status_code in (200, 201)


# ── Meta Pixel + CAPI header_scripts merger (parallel to GHL) ────────────────
# Lazily loads network-config.json once. Resolves settings.meta merged with
# per-site sites[i].meta and returns the Pixel snippet to prepend into <head>
# at publish time. Kept fully independent from the GHL injector.
_META_CFG_CACHE = {"loaded": False, "global": {}, "sites_by_id": {}}

def _meta_load_network_cfg():
    if _META_CFG_CACHE["loaded"]:
        return _META_CFG_CACHE
    try:
        cfg = json.loads((BASE / "network-config.json").read_text(encoding="utf-8"))
        _META_CFG_CACHE["global"] = (cfg.get("settings") or {}).get("meta") or {}
        _META_CFG_CACHE["sites_by_id"] = {
            (s.get("id") or ""): s for s in (cfg.get("sites") or [])
        }
    except Exception:
        _META_CFG_CACHE["global"] = {}
        _META_CFG_CACHE["sites_by_id"] = {}
    _META_CFG_CACHE["loaded"] = True
    return _META_CFG_CACHE

def _meta_resolve_for_site(site_obj_inline):
    """Merge global meta with per-site meta. site_obj_inline is the SITES dict
    used by push-sites; the per-site `meta` lives in network-config.json under
    sites[i].meta keyed by id, so we look it up there."""
    cache = _meta_load_network_cfg()
    g = cache["global"] or {}
    nc_site = cache["sites_by_id"].get((site_obj_inline or {}).get("id"), {}) or {}
    out = {
        "enabled":            bool(g.get("enabled", False)),
        "pixel_id":           str(g.get("pixel_id", "") or ""),
        "capi_token":         str(g.get("capi_token", "") or ""),
        "capi_dataset_id":    str(g.get("capi_dataset_id", "") or ""),
        "test_event_code":    str(g.get("test_event_code", "") or ""),
        "fire_pageview":      bool(g.get("fire_pageview", True)),
        "custom_audience_id": str(g.get("custom_audience_id", "") or ""),
    }
    s = nc_site.get("meta") or {}
    if not isinstance(s, dict):
        s = {}
    if "enabled" in s:        out["enabled"]       = bool(s.get("enabled"))
    if "fire_pageview" in s:  out["fire_pageview"] = bool(s.get("fire_pageview"))
    for k in ("pixel_id", "capi_token", "capi_dataset_id", "test_event_code", "custom_audience_id"):
        v = s.get(k)
        if isinstance(v, str) and v.strip():
            out[k] = v.strip()
    # Also surface site name for the custom event label
    out["_site_name"] = (site_obj_inline.get("name") or site_obj_inline.get("id") or "Site")
    out["_site_id"]   = site_obj_inline.get("id") or ""
    return out

def _meta_pixel_snippet(site_obj_inline):
    r = _meta_resolve_for_site(site_obj_inline)
    if not r["enabled"] or not r["pixel_id"]:
        return ""
    site_name  = r["_site_name"]
    site_id    = r["_site_id"]
    pixel_id   = r["pixel_id"]
    visit_evt  = f"{site_name} Visit"
    signup_evt = f"{site_name} NewsletterSignup"
    fire_pv    = "true" if r["fire_pageview"] else "false"
    mirror_capi = "true" if (r["capi_token"] and r["capi_dataset_id"]) else "false"
    return (
        "<!-- Meta Pixel (Kavalsia network) -->\n"
        "<script>\n"
        "(function(){if(window.__KAVALSIA_META_LOADED)return;window.__KAVALSIA_META_LOADED=true;"
        "!function(f,b,e,v,n,t,s){if(f.fbq)return;n=f.fbq=function(){n.callMethod?"
        "n.callMethod.apply(n,arguments):n.queue.push(arguments)};if(!f._fbq)f._fbq=n;"
        "n.push=n;n.loaded=!0;n.version='2.0';n.queue=[];t=b.createElement(e);t.async=!0;"
        "t.src=v;s=b.getElementsByTagName(e)[0];s.parentNode.insertBefore(t,s)}(window,"
        "document,'script','https://connect.facebook.net/en_US/fbevents.js');"
        f"fbq('init', {json.dumps(pixel_id)});"
        f"var FIRE_PV={fire_pv},SITE_ID={json.dumps(site_id)},VISIT_EVT={json.dumps(visit_evt)},"
        f"SIGNUP_EVT={json.dumps(signup_evt)},MIRROR_CAPI={mirror_capi};"
        "if(FIRE_PV){try{fbq('track','PageView');}catch(e){}}"
        "try{fbq('trackCustom',VISIT_EVT,{site_id:SITE_ID,page_path:location.pathname,"
        "page_title:document.title,referrer:document.referrer||''});}catch(e){}"
        "function sha256Hex(str){if(!window.crypto||!crypto.subtle)return Promise.resolve('');"
        "var buf=new TextEncoder().encode(String(str||'').trim().toLowerCase());"
        "return crypto.subtle.digest('SHA-256',buf).then(function(h){"
        "return Array.prototype.map.call(new Uint8Array(h),function(b){"
        "return ('00'+b.toString(16)).slice(-2);}).join('');});}"
        "function mirrorCAPI(evtName,payload){if(!MIRROR_CAPI)return;try{"
        "var hub=(window.KAVALSIA_HUB_URL||'').replace(/\\/$/,'');if(!hub)return;"
        "fetch(hub+'/api/meta-capi',{method:'POST',headers:{'Content-Type':'application/json'},"
        "body:JSON.stringify({site_id:SITE_ID,event_name:evtName,payload:payload})})"
        ".catch(function(){});}catch(e){}}"
        "mirrorCAPI(VISIT_EVT,{page_path:location.pathname});"
        "document.addEventListener('submit',function(ev){try{var f=ev.target;"
        "if(!f||!f.tagName||f.tagName.toLowerCase()!=='form')return;"
        "var emailEl=f.querySelector('input[type=email], input[name*=email i]');"
        "if(!emailEl||!emailEl.value)return;var email=emailEl.value;"
        "sha256Hex(email).then(function(h){try{fbq('trackCustom',SIGNUP_EVT,{email_hashed:h});}catch(e){}"
        "mirrorCAPI(SIGNUP_EVT,{email_hashed:h});});}catch(e){}},true);"
        "})();\n"
        "</script>\n"
        f"<noscript><img height=\"1\" width=\"1\" style=\"display:none\" alt=\"\" "
        f"src=\"https://www.facebook.com/tr?id={pixel_id}&ev=PageView&noscript=1\"/></noscript>\n"
        "<!-- End Meta Pixel -->\n"
    )

def _meta_inject(html, site_obj_inline):
    """Prepend the Meta Pixel snippet into <head> of the given html. No-op
    when Meta is disabled or no pixel is configured for the site."""
    if not html or not isinstance(html, str):
        return html
    snip = _meta_pixel_snippet(site_obj_inline)
    if not snip:
        return html
    if "</head>" in html:
        return html.replace("</head>", snip + "</head>", 1)
    return snip + html


# Niche assignment for the Nexus mosaic. Every site in network-config.json must
# have a niche id here that matches one of the NICHES entries in nexus.html.
# Add a one-line entry when a new site joins the network. Sites not in this map
# fall back to NEXUS_DEFAULT_NICHE so they still appear (just under a generic niche).
NEXUS_SITE_NICHES = {
  "cryptopulse":"finance","tradingtechreview":"finance","passivewealthguide":"finance","insightinsure":"finance",
  "sellit-ca":"realestate","mashestate-construction":"realestate",
  "aimarketingpro":"business","onlinebizpro":"business","ecommerceedge":"business","topproduct":"business",
  "fitpulsepro":"health","sportiqpro":"health","supplementverge":"health",
  "datingedge":"lifestyle","newborniq":"lifestyle","mochapoo-pets":"lifestyle",
  "dalmend-home":"home",
  "travelverge":"travel","kanona-events":"travel",
  "carverge":"auto",
  "makeupcraft":"beauty",
  "sightreadingacademy":"education",
  "mindframe":"wellness",
  "folioatelier":"arts",
  "modeformstudio":"fashion",
  "calibernotes":"watches",
  "crestcharter":"luxury",
  "strobeatlas":"nightlife",
}
NEXUS_DEFAULT_NICHE = "business"


def _sync_nexus_sites_array(html):
    """Rewrite the `const SITES=[ ... ];` block in nexus.html so every site in
    this module's SITES list appears in the Nexus mosaic. Source of truth is
    push-sites.py SITES (it has the canonical id, friendly name, and homepage
    accent color, all aligned with the template/repo). Niche comes from
    NEXUS_SITE_NICHES; unmapped sites fall back to NEXUS_DEFAULT_NICHE so they
    still appear. Add a new site to SITES + one line in NEXUS_SITE_NICHES and
    it shows up on Nexus the next push - no nexus.html edit needed."""
    import re as _re
    rows = []
    for s in SITES:
        sid = s.get("id")
        if not sid or sid == "nexus":
            continue
        name  = s.get("name") or sid
        niche = NEXUS_SITE_NICHES.get(sid, NEXUS_DEFAULT_NICHE)
        color = s.get("primary") or "#4f8ef7"
        rows.append(f"  {{id:'{sid}', name:'{name}', niche:'{niche}', color:'{color}'}}")
    new_block = "const SITES=[\n" + ",\n".join(rows) + "\n];"
    new_html, n = _re.subn(r"const SITES\s*=\s*\[[\s\S]*?\];", new_block, html, count=1)
    if n == 0:
        new_html = html.replace("</script>", new_block + "\n</script>", 1)
    return new_html


def _sync_nexus_count(html):
    """Replace every hardcoded publishing-site count in Nexus's homepage and
    about page with the live count derived from SITES. Works regardless of
    what the prior baked-in value was (was 28 in nexus.html, 22 in about.html).
    Source of truth = number of non-nexus sites in SITES. Safe: only replaces
    digits in publication-count contexts (followed by 'publications', 'sites',
    'expert voices', etc.), not in CSS values, rgba alphas, font sizes, or
    arbitrary tags."""
    import re as _re
    site_count  = sum(1 for s in SITES if s.get("id") and s.get("id") != "nexus")
    sc = str(site_count)
    patterns = [
        # 'N publications', 'N sites', 'N specialized', 'N niche', 'N Publications',
        # 'N Nexus publications', 'N expert voices'
        (r'\b\d+(\s+(?:publications?|sites?|specialized|niche|Nexus\s+publications|Publications|expert\s+voices))', rf'{sc}\1'),
        # data-target="N" ONLY when followed by a "Publications" stat label
        # (don't touch the Niches/Articles/Continents stat counters).
        (r'(data-target=")\d+("[^>]*>0</div>\s*<div[^>]*class="stat-lbl"[^>]*>Publications)', rf'\g<1>{sc}\g<2>'),
        # <strong>N</strong> sites  (header nav badge)
        (r'(<strong[^>]*>)\d+(</strong>\s*sites)', rf'\g<1>{sc}\g<2>'),
        # <b>N</b> ...Publications  (stat tile where the label "Publications"
        # follows shortly after the bolded number)
        (r'(<b[^>]*>)\d+(</b>(?:(?!</?div\s+class).){0,200}?Publications)', rf'\g<1>{sc}\g<2>'),
    ]
    for pat, rep in patterns:
        html = _re.sub(pat, rep, html, flags=_re.DOTALL)
    return html


def push_nexus(token):
    """Push the Nexus mother site (nexus.html + about.html) to Siavashsed/nexus."""
    import json as _json
    repo = "Siavashsed/nexus"
    nexus_src  = Path(__file__).parent / "nexus.html"
    about_src  = Path(__file__).parent / "about.html"
    cfg_path   = Path(__file__).parent / "network-config.json"
    print(f"  Pushing {repo} (Nexus Mother Site)...", end=" ", flush=True)
    ok = True
    if nexus_src.exists():
        html = nexus_src.read_text()
        # Auto-sync the in-page SITES array to network-config.json so any newly
        # added site appears in the Nexus mosaic without a manual nexus.html edit.
        html = _sync_nexus_sites_array(html)
        # Auto-sync the hardcoded publishing-site count (legacy '28') so adding
        # more sites updates the header, footer, hero, stats, and meta tags too.
        html = _sync_nexus_count(html)
        # Inject hub API URL so the subscribe form knows where to POST
        hub_url = ""
        if cfg_path.exists():
            try:
                hub_url = _json.loads(cfg_path.read_text()).get("settings", {}).get("hub_api_url", "")
            except Exception:
                pass
        inject = f'<script>var KAVALSIA_HUB_URL="{hub_url}";</script>'
        html = html.replace("</head>", inject + "\n</head>", 1)
        ok &= gh_put(token, repo, "index.html", html, "Update Nexus hub")
    if about_src.exists():
        about_html = about_src.read_text()
        # Same dynamic-count rewrite applied to the about page so its hero,
        # stat tile, footer, and meta description stay in sync with SITES.
        about_html = _sync_nexus_count(about_html)
        ok &= gh_put(token, repo, "about.html", about_html, "Update Nexus about")
    ok &= gh_put(token, repo, ".nojekyll", "", "Disable Jekyll")
    # NOTE: do NOT auto-delete CNAME - if the user has a custom domain, that file
    # is what binds it. The previous gh_delete here was wiping live custom domains.
    print("ok" if ok else "FAIL (check token/repo)")


def push_github(token, only=None, sites_filter=None):
    filt = set(sites_filter) if sites_filter else ({only} if only else None)

    # Always push Nexus mother site unless filtering to specific non-nexus sites
    if not filt or "nexus" in filt:
        push_nexus(token)
        time.sleep(0.8)

    # Dedupe by repo - SITES historically carries some entries twice (legacy
    # id like "passivewealthguide" + modern id like "passive-wealth" pointing
    # at the same repo). Pushing the same repo twice in one run is wasteful
    # and the second hit usually has no matching template - which is why
    # crashes show up as "Template not found: <modern-id>-index.html".
    pushed_repos = set()
    for s in SITES:
        if filt and s["id"] not in filt:
            continue
        repo = s.get("repo", "")
        if repo in pushed_repos:
            continue
        pushed_repos.add(repo)
        try:
            idx, abt = generate(s)
        except FileNotFoundError as _ex:
            # No template for this entry - happens when SITES has a stale
            # duplicate entry pointing at a repo whose template is keyed
            # on a sibling entry. Skip rather than crash the whole run.
            print(f"  Skipping {repo} ({s['id']}): {_ex}")
            continue
        print(f"  Pushing {repo}...", end=" ", flush=True)
        ok = True
        ok &= gh_put(token, repo, "index.html",       _meta_inject(idx, s),                 "Update site index")
        ok &= gh_put(token, repo, "about.html",        _meta_inject(abt, s),                "Update about page")
        ok &= gh_put(token, repo, "404.html",          _meta_inject(gen_404(s), s),         "Update 404 page")
        ok &= gh_put(token, repo, "privacy.html",      _meta_inject(gen_privacy(s), s),     "Add privacy policy")
        ok &= gh_put(token, repo, "terms.html",        _meta_inject(gen_terms(s), s),       "Add terms and conditions")
        ok &= gh_put(token, repo, "sms.html",          _meta_inject(gen_sms(s), s),         "Add SMS compliance policy")
        ok &= gh_put(token, repo, "meta-policy.html",  _meta_inject(gen_meta_policy(s), s), "Add Meta data policy")
        # Path is articles/index.html so the URL resolves with or without
        # trailing slash; bare articles.html 404s the /articles/ form.
        ok &= gh_put(token, repo, "articles/index.html", _meta_inject(gen_articles_index(s), s), "Add all-articles index")
        for fn, html in extra_pages(s):
            ok &= gh_put(token, repo, fn, _meta_inject(html, s), f"Add {fn}")
        ok &= gh_put(token, repo, ".nojekyll",         "",               "Disable Jekyll")
        # CNAME is intentionally NOT deleted - it carries the custom-domain binding
        # for GitHub Pages. Wiping it here previously broke live domains on every sync.
        print("ok" if ok else "FAIL (check token/repo)")
        time.sleep(0.8)
    print("\nDone.")


# ── Main ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Kavalsia site template generator")
    p.add_argument("--save",  action="store_true", help="Save to site-templates/")
    p.add_argument("--push",  metavar="TOKEN",     help="Push to GitHub with this token")
    p.add_argument("--only",  metavar="SITE_ID",   help="Only process this one site ID")
    p.add_argument("--sites", metavar="ID1,ID2",   help="Comma-separated site IDs to process")
    args = p.parse_args()

    if not args.save and not args.push:
        p.print_help()
        sys.exit(0)

    sites_filter = [x.strip() for x in args.sites.split(",")] if args.sites else None

    if args.save:
        print("\nSaving templates locally…")
        save_local(only=args.only, sites_filter=sites_filter)

    if args.push:
        print("\nPushing to GitHub…")
        push_github(args.push, only=args.only, sites_filter=sites_filter)
