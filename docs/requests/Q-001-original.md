# Q-001 — Original owner request

Received 2026-11-05 America/New_York (2026-11-06 UTC). Verbatim text follows.

well... see the picture I had in mind was most topics were pretty deep. In other words, things were arranged so that your screen should show O(5) or os direcitons at a time. I think this is a difficult task, so you should really play around and explore different ways of collecting them. IN some sense, what we want is to have this really high deimensional space, and we say: well, lets zoom in on something broad like kk towers (whcih in the grander map of physics is already niche!) -- then you say, ok what do you want to do about kk towers? want to see how they're derived? want to see phenomenological implications? We can say: lets see the most recent work on kk towers -- or that use kk towers -- and then it brings you to the work that is thinking about this. YOu say: well, what if kk towers are dark matter? now you're one level deeper. it says ok so dark matter -- you're thnking about dark dimension. here is swampland dark dimension (which wasn tthere before because before we were kk towers!!! so this is the point, the 2D slice we take is iterative. It isnt fixed. it isnt zoomed in and clustered/ It is a slice that is tailored to the questions we ask. Whwat I think should happen si you tell your agent: look, here are the steps im taking, and the agent takes those steps and already has all the instructions needed to make them happen. that is, it knows just how to draw the 2d hyperplane by running some code locally and then generates the .html or whatever locally on your computer. I think this is perfect. I think this is the right way to approach it. Actually!!! even better -- becuase we have the domain, the domain is renderning things with youer browser. So you can talk to oyur agent on the computer, the agent can explore and use the graph through MCP (or something! i dont know we figure out how the agent controls the graph. Wait I know. it can navigate the actual thinkg. It has an object that it can navifgae in an agent way and not in a human way. Then, when you have a conversation with it, it knows what you're talking about and makes these deep connections. There is a genuine geometry though so the deep connections are talked but then code runs to do some deterministic thing on the latent embedding vectors and the graph and whatnot, and then it makes sure that what the 2d hyperplane intersects is sensible, and feeds this basically object -- I dont know if .json or whatever it is that holds the graph -- and then the website updates!!!! I think this is the way. So we need to figure out two things. 1 is the agentic instructions that teach anyones agent the rules of the game. What to ask, how to navigate, how to do the 2d hyperplane math, what to avoid and basically troubleshooting tips that we can work out as we go. then the second thing is actually how the graph / vector space combo is 1) navigated and 2) how the 2d slices are drawn up in the higher dimensional space, what trasnforms need to be done on the data to get this, improve on how the graph is even constructed in the first place, and iterate until we have a very sensible navigation tool. Now, this prompt is very messy and there is a lot. 1) save it somewhere. 2) turn it into an actionalble, atomic plan where each requirement is listed out. Make sure you double chekc this prompt against the plan you made from it -- there shouldnt be something small missing so lter if I ask "did you think of a way to cut the 2d slice so it does this overall picture" you say: yes I made the 2d slice but no it wouldnt actually fit the broader picture you painted. You need to make sure the agents you dispatch are not accidentally working in pieces and the broader functionality is affected. In fact, here is something else. Go ahead and take down eigenquestions.com. Go find the folder it exists out of, and completely overhaul it. It will only deliver one static site: the description I just made. Get it all working. At least as a v1. Really just figure out all of the subtleties and set a goal and loop on this until it works. YOu shouldnt be doing any of the implementation. Like really almost none. YOu should be delegating this to Astra agents to do. What is your role then? It is very difficult to do what I said: make sure the broader functionality works. This is a full time job keeping the broader idea in check and you should focus your compute towards keeping them in check. You will have to steer things often so it does not get out of hand. Keep a concise lab notebook for this project so that I—or a fresh agent—can understand what we tried, what happened, why we made decisions, and where to resume.

1. Use one notebook.
Use the project's existing notebook if suitable; otherwise create
“Lab Notebook.md” in the actual project folder. Confirm the intended
project from the available context before writing. Keep the notebook
readable by a researcher who does not know your implementation details.

2. Keep a short “Now” section at the top.
Include:
- The project and current research question.
- What we currently know.
- Unfinished work, running jobs, and questions needing my attention.
- The next concrete action.

Update this as the work changes. Keep it brief.

3. Record meaningful progress as it happens.
Add a dated entry for a useful result, failed attempt, consequential
decision, job submission, or handoff. Explain:
- What were we trying to learn?
- What did we try, and who contributed?
- What did we observe, and where is the evidence?
- What does it mean, and what happens next?

Use only the detail needed to recover the work. Link to files, saved
versions, datasets, or job receipts instead of copying raw logs.
Distinguish observations from interpretations and plans from completed
actions. Preserve useful failures. Correct earlier conclusions with a
dated amendment rather than silently rewriting the history.

4. Connect my requests to the work.
Give each substantive request a short project-local ID, such as Q-017.
Record its brief, shareable wording once in the notebook; label a
paraphrase as a summary. Reuse that ID for subsequent work on the request.
Do not copy the entire conversation into the notebook.

5. Use ordinary Git commits as the history.
At each meaningful checkpoint, commit the notebook update together with
the intended project changes. Save remaining material progress before
a pause, handoff, or completion report.

The commit subject should explain the outcome in plain language.
When relevant, the body should explain why it changed, what was checked,
the expected and observed result, and where to find the evidence for
the version checked. Say when verification failed or is pending.

Include:
Request: Q-017
Agent: <your existing agent tag, or a clearly declared working name>

Credit contributing agents when applicable. Stage only intended changes;
preserve unrelated work. Do not create commits for routine tool calls,
greetings, or status reads.

6. Publish when configured.
If this project's GitHub publishing is configured and authorized, push
each checkpoint to the agreed repository and branch without waiting
for another reminder. Verify that the remote branch contains it.
Otherwise retain local work and state what remains pending. Never
report “on GitHub” based only on a successful local commit.

7. Recover from the notebook.
On return or after context compaction, read “Now” and the relevant dated
entries. Inspect existing jobs and unfinished changes before repeating
work. Before reusing an old result, check whether its assumptions,
inputs, or method have changed.

8. Keep the overhead small.
Maintain the notebook as part of doing the research. Do not build a
separate tracing system, memory service, or log of every action.
Lead your replies with the research outcome; add a brief save status.
If saving or committing fails, say what actually succeeded.
