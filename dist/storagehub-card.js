function t(t,e,s,i){var n,r=arguments.length,o=r<3?e:null===i?i=Object.getOwnPropertyDescriptor(e,s):i;if("object"==typeof Reflect&&"function"==typeof Reflect.decorate)o=Reflect.decorate(t,e,s,i);else for(var a=t.length-1;a>=0;a--)(n=t[a])&&(o=(r<3?n(o):r>3?n(e,s,o):n(e,s))||o);return r>3&&o&&Object.defineProperty(e,s,o),o}"function"==typeof SuppressedError&&SuppressedError;
/**
 * @license
 * Copyright 2019 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */
const e=globalThis,s=e.ShadowRoot&&(void 0===e.ShadyCSS||e.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,i=Symbol(),n=new WeakMap;let r=class{constructor(t,e,s){if(this._$cssResult$=!0,s!==i)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=t,this.t=e}get styleSheet(){let t=this.o;const e=this.t;if(s&&void 0===t){const s=void 0!==e&&1===e.length;s&&(t=n.get(e)),void 0===t&&((this.o=t=new CSSStyleSheet).replaceSync(this.cssText),s&&n.set(e,t))}return t}toString(){return this.cssText}};const o=s?t=>t:t=>t instanceof CSSStyleSheet?(t=>{let e="";for(const s of t.cssRules)e+=s.cssText;return(t=>new r("string"==typeof t?t:t+"",void 0,i))(e)})(t):t,{is:a,defineProperty:c,getOwnPropertyDescriptor:l,getOwnPropertyNames:h,getOwnPropertySymbols:d,getPrototypeOf:u}=Object,p=globalThis,_=p.trustedTypes,m=_?_.emptyScript:"",f=p.reactiveElementPolyfillSupport,$=(t,e)=>t,g={toAttribute(t,e){switch(e){case Boolean:t=t?m:null;break;case Object:case Array:t=null==t?t:JSON.stringify(t)}return t},fromAttribute(t,e){let s=t;switch(e){case Boolean:s=null!==t;break;case Number:s=null===t?null:Number(t);break;case Object:case Array:try{s=JSON.parse(t)}catch(t){s=null}}return s}},y=(t,e)=>!a(t,e),v={attribute:!0,type:String,converter:g,reflect:!1,useDefault:!1,hasChanged:y};
/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */Symbol.metadata??=Symbol("metadata"),p.litPropertyMetadata??=new WeakMap;let b=class extends HTMLElement{static addInitializer(t){this._$Ei(),(this.l??=[]).push(t)}static get observedAttributes(){return this.finalize(),this._$Eh&&[...this._$Eh.keys()]}static createProperty(t,e=v){if(e.state&&(e.attribute=!1),this._$Ei(),this.prototype.hasOwnProperty(t)&&((e=Object.create(e)).wrapped=!0),this.elementProperties.set(t,e),!e.noAccessor){const s=Symbol(),i=this.getPropertyDescriptor(t,s,e);void 0!==i&&c(this.prototype,t,i)}}static getPropertyDescriptor(t,e,s){const{get:i,set:n}=l(this.prototype,t)??{get(){return this[e]},set(t){this[e]=t}};return{get:i,set(e){const r=i?.call(this);n?.call(this,e),this.requestUpdate(t,r,s)},configurable:!0,enumerable:!0}}static getPropertyOptions(t){return this.elementProperties.get(t)??v}static _$Ei(){if(this.hasOwnProperty($("elementProperties")))return;const t=u(this);t.finalize(),void 0!==t.l&&(this.l=[...t.l]),this.elementProperties=new Map(t.elementProperties)}static finalize(){if(this.hasOwnProperty($("finalized")))return;if(this.finalized=!0,this._$Ei(),this.hasOwnProperty($("properties"))){const t=this.properties,e=[...h(t),...d(t)];for(const s of e)this.createProperty(s,t[s])}const t=this[Symbol.metadata];if(null!==t){const e=litPropertyMetadata.get(t);if(void 0!==e)for(const[t,s]of e)this.elementProperties.set(t,s)}this._$Eh=new Map;for(const[t,e]of this.elementProperties){const s=this._$Eu(t,e);void 0!==s&&this._$Eh.set(s,t)}this.elementStyles=this.finalizeStyles(this.styles)}static finalizeStyles(t){const e=[];if(Array.isArray(t)){const s=new Set(t.flat(1/0).reverse());for(const t of s)e.unshift(o(t))}else void 0!==t&&e.push(o(t));return e}static _$Eu(t,e){const s=e.attribute;return!1===s?void 0:"string"==typeof s?s:"string"==typeof t?t.toLowerCase():void 0}constructor(){super(),this._$Ep=void 0,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Em=null,this._$Ev()}_$Ev(){this._$ES=new Promise(t=>this.enableUpdating=t),this._$AL=new Map,this._$E_(),this.requestUpdate(),this.constructor.l?.forEach(t=>t(this))}addController(t){(this._$EO??=new Set).add(t),void 0!==this.renderRoot&&this.isConnected&&t.hostConnected?.()}removeController(t){this._$EO?.delete(t)}_$E_(){const t=new Map,e=this.constructor.elementProperties;for(const s of e.keys())this.hasOwnProperty(s)&&(t.set(s,this[s]),delete this[s]);t.size>0&&(this._$Ep=t)}createRenderRoot(){const t=this.shadowRoot??this.attachShadow(this.constructor.shadowRootOptions);return((t,i)=>{if(s)t.adoptedStyleSheets=i.map(t=>t instanceof CSSStyleSheet?t:t.styleSheet);else for(const s of i){const i=document.createElement("style"),n=e.litNonce;void 0!==n&&i.setAttribute("nonce",n),i.textContent=s.cssText,t.appendChild(i)}})(t,this.constructor.elementStyles),t}connectedCallback(){this.renderRoot??=this.createRenderRoot(),this.enableUpdating(!0),this._$EO?.forEach(t=>t.hostConnected?.())}enableUpdating(t){}disconnectedCallback(){this._$EO?.forEach(t=>t.hostDisconnected?.())}attributeChangedCallback(t,e,s){this._$AK(t,s)}_$ET(t,e){const s=this.constructor.elementProperties.get(t),i=this.constructor._$Eu(t,s);if(void 0!==i&&!0===s.reflect){const n=(void 0!==s.converter?.toAttribute?s.converter:g).toAttribute(e,s.type);this._$Em=t,null==n?this.removeAttribute(i):this.setAttribute(i,n),this._$Em=null}}_$AK(t,e){const s=this.constructor,i=s._$Eh.get(t);if(void 0!==i&&this._$Em!==i){const t=s.getPropertyOptions(i),n="function"==typeof t.converter?{fromAttribute:t.converter}:void 0!==t.converter?.fromAttribute?t.converter:g;this._$Em=i;const r=n.fromAttribute(e,t.type);this[i]=r??this._$Ej?.get(i)??r,this._$Em=null}}requestUpdate(t,e,s,i=!1,n){if(void 0!==t){const r=this.constructor;if(!1===i&&(n=this[t]),s??=r.getPropertyOptions(t),!((s.hasChanged??y)(n,e)||s.useDefault&&s.reflect&&n===this._$Ej?.get(t)&&!this.hasAttribute(r._$Eu(t,s))))return;this.C(t,e,s)}!1===this.isUpdatePending&&(this._$ES=this._$EP())}C(t,e,{useDefault:s,reflect:i,wrapped:n},r){s&&!(this._$Ej??=new Map).has(t)&&(this._$Ej.set(t,r??e??this[t]),!0!==n||void 0!==r)||(this._$AL.has(t)||(this.hasUpdated||s||(e=void 0),this._$AL.set(t,e)),!0===i&&this._$Em!==t&&(this._$Eq??=new Set).add(t))}async _$EP(){this.isUpdatePending=!0;try{await this._$ES}catch(t){Promise.reject(t)}const t=this.scheduleUpdate();return null!=t&&await t,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){if(!this.isUpdatePending)return;if(!this.hasUpdated){if(this.renderRoot??=this.createRenderRoot(),this._$Ep){for(const[t,e]of this._$Ep)this[t]=e;this._$Ep=void 0}const t=this.constructor.elementProperties;if(t.size>0)for(const[e,s]of t){const{wrapped:t}=s,i=this[e];!0!==t||this._$AL.has(e)||void 0===i||this.C(e,void 0,s,i)}}let t=!1;const e=this._$AL;try{t=this.shouldUpdate(e),t?(this.willUpdate(e),this._$EO?.forEach(t=>t.hostUpdate?.()),this.update(e)):this._$EM()}catch(e){throw t=!1,this._$EM(),e}t&&this._$AE(e)}willUpdate(t){}_$AE(t){this._$EO?.forEach(t=>t.hostUpdated?.()),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(t)),this.updated(t)}_$EM(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$ES}shouldUpdate(t){return!0}update(t){this._$Eq&&=this._$Eq.forEach(t=>this._$ET(t,this[t])),this._$EM()}updated(t){}firstUpdated(t){}};b.elementStyles=[],b.shadowRootOptions={mode:"open"},b[$("elementProperties")]=new Map,b[$("finalized")]=new Map,f?.({ReactiveElement:b}),(p.reactiveElementVersions??=[]).push("2.1.2");
/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */
const w=globalThis,A=t=>t,x=w.trustedTypes,E=x?x.createPolicy("lit-html",{createHTML:t=>t}):void 0,S="$lit$",C=`lit$${Math.random().toFixed(9).slice(2)}$`,P="?"+C,R=`<${P}>`,k=document,H=()=>k.createComment(""),T=t=>null===t||"object"!=typeof t&&"function"!=typeof t,U=Array.isArray,O="[ \t\n\f\r]",M=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,N=/-->/g,L=/>/g,I=RegExp(`>|${O}(?:([^\\s"'>=/]+)(${O}*=${O}*(?:[^ \t\n\f\r"'\`<>=]|("|')|))|$)`,"g"),z=/'/g,j=/"/g,q=/^(?:script|style|textarea|title)$/i,D=(t=>(e,...s)=>({_$litType$:t,strings:e,values:s}))(1),B=Symbol.for("lit-noChange"),W=Symbol.for("lit-nothing"),V=new WeakMap,G=k.createTreeWalker(k,129);function K(t,e){if(!U(t)||!t.hasOwnProperty("raw"))throw Error("invalid template strings array");return void 0!==E?E.createHTML(e):e}const J=(t,e)=>{const s=t.length-1,i=[];let n,r=2===e?"<svg>":3===e?"<math>":"",o=M;for(let e=0;e<s;e++){const s=t[e];let a,c,l=-1,h=0;for(;h<s.length&&(o.lastIndex=h,c=o.exec(s),null!==c);)h=o.lastIndex,o===M?"!--"===c[1]?o=N:void 0!==c[1]?o=L:void 0!==c[2]?(q.test(c[2])&&(n=RegExp("</"+c[2],"g")),o=I):void 0!==c[3]&&(o=I):o===I?">"===c[0]?(o=n??M,l=-1):void 0===c[1]?l=-2:(l=o.lastIndex-c[2].length,a=c[1],o=void 0===c[3]?I:'"'===c[3]?j:z):o===j||o===z?o=I:o===N||o===L?o=M:(o=I,n=void 0);const d=o===I&&t[e+1].startsWith("/>")?" ":"";r+=o===M?s+R:l>=0?(i.push(a),s.slice(0,l)+S+s.slice(l)+C+d):s+C+(-2===l?e:d)}return[K(t,r+(t[s]||"<?>")+(2===e?"</svg>":3===e?"</math>":"")),i]};class Z{constructor({strings:t,_$litType$:e},s){let i;this.parts=[];let n=0,r=0;const o=t.length-1,a=this.parts,[c,l]=J(t,e);if(this.el=Z.createElement(c,s),G.currentNode=this.el.content,2===e||3===e){const t=this.el.content.firstChild;t.replaceWith(...t.childNodes)}for(;null!==(i=G.nextNode())&&a.length<o;){if(1===i.nodeType){if(i.hasAttributes())for(const t of i.getAttributeNames())if(t.endsWith(S)){const e=l[r++],s=i.getAttribute(t).split(C),o=/([.?@])?(.*)/.exec(e);a.push({type:1,index:n,name:o[2],strings:s,ctor:"."===o[1]?tt:"?"===o[1]?et:"@"===o[1]?st:Y}),i.removeAttribute(t)}else t.startsWith(C)&&(a.push({type:6,index:n}),i.removeAttribute(t));if(q.test(i.tagName)){const t=i.textContent.split(C),e=t.length-1;if(e>0){i.textContent=x?x.emptyScript:"";for(let s=0;s<e;s++)i.append(t[s],H()),G.nextNode(),a.push({type:2,index:++n});i.append(t[e],H())}}}else if(8===i.nodeType)if(i.data===P)a.push({type:2,index:n});else{let t=-1;for(;-1!==(t=i.data.indexOf(C,t+1));)a.push({type:7,index:n}),t+=C.length-1}n++}}static createElement(t,e){const s=k.createElement("template");return s.innerHTML=t,s}}function F(t,e,s=t,i){if(e===B)return e;let n=void 0!==i?s._$Co?.[i]:s._$Cl;const r=T(e)?void 0:e._$litDirective$;return n?.constructor!==r&&(n?._$AO?.(!1),void 0===r?n=void 0:(n=new r(t),n._$AT(t,s,i)),void 0!==i?(s._$Co??=[])[i]=n:s._$Cl=n),void 0!==n&&(e=F(t,n._$AS(t,e.values),n,i)),e}class Q{constructor(t,e){this._$AV=[],this._$AN=void 0,this._$AD=t,this._$AM=e}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(t){const{el:{content:e},parts:s}=this._$AD,i=(t?.creationScope??k).importNode(e,!0);G.currentNode=i;let n=G.nextNode(),r=0,o=0,a=s[0];for(;void 0!==a;){if(r===a.index){let e;2===a.type?e=new X(n,n.nextSibling,this,t):1===a.type?e=new a.ctor(n,a.name,a.strings,this,t):6===a.type&&(e=new it(n,this,t)),this._$AV.push(e),a=s[++o]}r!==a?.index&&(n=G.nextNode(),r++)}return G.currentNode=k,i}p(t){let e=0;for(const s of this._$AV)void 0!==s&&(void 0!==s.strings?(s._$AI(t,s,e),e+=s.strings.length-2):s._$AI(t[e])),e++}}class X{get _$AU(){return this._$AM?._$AU??this._$Cv}constructor(t,e,s,i){this.type=2,this._$AH=W,this._$AN=void 0,this._$AA=t,this._$AB=e,this._$AM=s,this.options=i,this._$Cv=i?.isConnected??!0}get parentNode(){let t=this._$AA.parentNode;const e=this._$AM;return void 0!==e&&11===t?.nodeType&&(t=e.parentNode),t}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(t,e=this){t=F(this,t,e),T(t)?t===W||null==t||""===t?(this._$AH!==W&&this._$AR(),this._$AH=W):t!==this._$AH&&t!==B&&this._(t):void 0!==t._$litType$?this.$(t):void 0!==t.nodeType?this.T(t):(t=>U(t)||"function"==typeof t?.[Symbol.iterator])(t)?this.k(t):this._(t)}O(t){return this._$AA.parentNode.insertBefore(t,this._$AB)}T(t){this._$AH!==t&&(this._$AR(),this._$AH=this.O(t))}_(t){this._$AH!==W&&T(this._$AH)?this._$AA.nextSibling.data=t:this.T(k.createTextNode(t)),this._$AH=t}$(t){const{values:e,_$litType$:s}=t,i="number"==typeof s?this._$AC(t):(void 0===s.el&&(s.el=Z.createElement(K(s.h,s.h[0]),this.options)),s);if(this._$AH?._$AD===i)this._$AH.p(e);else{const t=new Q(i,this),s=t.u(this.options);t.p(e),this.T(s),this._$AH=t}}_$AC(t){let e=V.get(t.strings);return void 0===e&&V.set(t.strings,e=new Z(t)),e}k(t){U(this._$AH)||(this._$AH=[],this._$AR());const e=this._$AH;let s,i=0;for(const n of t)i===e.length?e.push(s=new X(this.O(H()),this.O(H()),this,this.options)):s=e[i],s._$AI(n),i++;i<e.length&&(this._$AR(s&&s._$AB.nextSibling,i),e.length=i)}_$AR(t=this._$AA.nextSibling,e){for(this._$AP?.(!1,!0,e);t!==this._$AB;){const e=A(t).nextSibling;A(t).remove(),t=e}}setConnected(t){void 0===this._$AM&&(this._$Cv=t,this._$AP?.(t))}}class Y{get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}constructor(t,e,s,i,n){this.type=1,this._$AH=W,this._$AN=void 0,this.element=t,this.name=e,this._$AM=i,this.options=n,s.length>2||""!==s[0]||""!==s[1]?(this._$AH=Array(s.length-1).fill(new String),this.strings=s):this._$AH=W}_$AI(t,e=this,s,i){const n=this.strings;let r=!1;if(void 0===n)t=F(this,t,e,0),r=!T(t)||t!==this._$AH&&t!==B,r&&(this._$AH=t);else{const i=t;let o,a;for(t=n[0],o=0;o<n.length-1;o++)a=F(this,i[s+o],e,o),a===B&&(a=this._$AH[o]),r||=!T(a)||a!==this._$AH[o],a===W?t=W:t!==W&&(t+=(a??"")+n[o+1]),this._$AH[o]=a}r&&!i&&this.j(t)}j(t){t===W?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,t??"")}}class tt extends Y{constructor(){super(...arguments),this.type=3}j(t){this.element[this.name]=t===W?void 0:t}}class et extends Y{constructor(){super(...arguments),this.type=4}j(t){this.element.toggleAttribute(this.name,!!t&&t!==W)}}class st extends Y{constructor(t,e,s,i,n){super(t,e,s,i,n),this.type=5}_$AI(t,e=this){if((t=F(this,t,e,0)??W)===B)return;const s=this._$AH,i=t===W&&s!==W||t.capture!==s.capture||t.once!==s.once||t.passive!==s.passive,n=t!==W&&(s===W||i);i&&this.element.removeEventListener(this.name,this,s),n&&this.element.addEventListener(this.name,this,t),this._$AH=t}handleEvent(t){"function"==typeof this._$AH?this._$AH.call(this.options?.host??this.element,t):this._$AH.handleEvent(t)}}class it{constructor(t,e,s){this.element=t,this.type=6,this._$AN=void 0,this._$AM=e,this.options=s}get _$AU(){return this._$AM._$AU}_$AI(t){F(this,t)}}const nt=w.litHtmlPolyfillSupport;nt?.(Z,X),(w.litHtmlVersions??=[]).push("3.3.2");const rt=globalThis;
/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */class ot extends b{constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){const t=super.createRenderRoot();return this.renderOptions.renderBefore??=t.firstChild,t}update(t){const e=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(t),this._$Do=((t,e,s)=>{const i=s?.renderBefore??e;let n=i._$litPart$;if(void 0===n){const t=s?.renderBefore??null;i._$litPart$=n=new X(e.insertBefore(H(),t),t,void 0,s??{})}return n._$AI(t),n})(e,this.renderRoot,this.renderOptions)}connectedCallback(){super.connectedCallback(),this._$Do?.setConnected(!0)}disconnectedCallback(){super.disconnectedCallback(),this._$Do?.setConnected(!1)}render(){return B}}ot._$litElement$=!0,ot.finalized=!0,rt.litElementHydrateSupport?.({LitElement:ot});const at=rt.litElementPolyfillSupport;at?.({LitElement:ot}),(rt.litElementVersions??=[]).push("4.2.2");
/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */
const ct={attribute:!0,type:String,converter:g,reflect:!1,hasChanged:y},lt=(t=ct,e,s)=>{const{kind:i,metadata:n}=s;let r=globalThis.litPropertyMetadata.get(n);if(void 0===r&&globalThis.litPropertyMetadata.set(n,r=new Map),"setter"===i&&((t=Object.create(t)).wrapped=!0),r.set(s.name,t),"accessor"===i){const{name:i}=s;return{set(s){const n=e.get.call(this);e.set.call(this,s),this.requestUpdate(i,n,t,!0,s)},init(e){return void 0!==e&&this.C(i,void 0,t,e),e}}}if("setter"===i){const{name:i}=s;return function(s){const n=this[i];e.call(this,s),this.requestUpdate(i,n,t,!0,s)}}throw Error("Unsupported decorator location: "+i)};
/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */function ht(t){return(e,s)=>"object"==typeof s?lt(t,e,s):((t,e,s)=>{const i=e.hasOwnProperty(s);return e.constructor.createProperty(s,t),i?Object.getOwnPropertyDescriptor(e,s):void 0})(t,e,s)}
/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */function dt(t){return ht({...t,state:!0,attribute:!1})}const ut=/[^\p{L}\p{N}\s]/gu;function pt(t){return t.toLowerCase().replace(ut," ").split(/\s+/).filter(t=>t.length>0)}function _t(t){const e=t.name.toLowerCase(),s=(t.owner_name??"").toLowerCase(),i=(t.container_name??"").toLowerCase(),n=(t.location_name??"").toLowerCase();return{entry:t,nameLc:e,nameTokens:pt(t.name),ownerLc:s,ownerTokens:pt(t.owner_name??""),containerLc:i,containerTokens:pt(t.container_name??""),locationLc:n,locationTokens:pt(t.location_name??""),aiNames:t.ai_names.map(t=>({lc:t.toLowerCase(),tokens:pt(t)}))}}function mt(t,e,s,i){if(0===e.length||!e.includes(t))return 0;let n=1;return e.startsWith(t)||s.some(e=>e.startsWith(t))?n=1.5:s.some(s=>s.includes(t)&&s!==e)&&(n=1.2),i*n}function ft(t,e){let s=0;for(const{lc:i,tokens:n}of e){const e=mt(t,i,n,8);e>s&&(s=e)}return s}function $t(t,e){let s=0;for(const i of e){const e=Math.max(mt(i,t.nameLc,t.nameTokens,10),mt(i,t.ownerLc,t.ownerTokens,6),mt(i,t.containerLc,t.containerTokens,4),mt(i,t.locationLc,t.locationTokens,3),ft(i,t.aiNames));if(0===e)return 0;s+=e}return s}class gt{constructor(t){this.entries=t.map(_t)}get size(){return this.entries.length}search(t,e){const s=pt(t);if(0===s.length)return[];if(s.every(t=>t.length<2))return[];const i=[];for(const t of this.entries){const e=$t(t,s);e>0&&i.push({entry:t.entry,score:e})}return i.sort((t,e)=>e.score!==t.score?e.score-t.score:t.entry.name.localeCompare(e.entry.name)),i.slice(0,e)}}const yt=((t,...e)=>{const s=1===t.length?t[0]:e.reduce((e,s,i)=>e+(t=>{if(!0===t._$cssResult$)return t.cssText;if("number"==typeof t)return t;throw Error("Value passed to 'css' function must be a 'css' function result: "+t+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(s)+t[i+1],t[0]);return new r(s,t,i)})`
  :host {
    display: block;
  }

  ha-card {
    padding: 12px 16px;
  }

  .search-input {
    width: 100%;
    padding: 10px 12px;
    font-size: 16px;
    border: 1px solid var(--divider-color, #e0e0e0);
    border-radius: var(--ha-card-border-radius, 8px);
    background: var(--card-background-color, #fff);
    color: var(--primary-text-color, #212121);
    box-sizing: border-box;
    outline: none;
    transition: border-color 120ms ease;
  }
  .search-input:focus {
    border-color: var(--primary-color, #03a9f4);
  }

  .empty,
  .loading,
  .error {
    padding: 16px 4px;
    color: var(--secondary-text-color, #727272);
    font-size: 14px;
    text-align: center;
  }
  .error {
    color: var(--error-color, #db4437);
  }

  .results {
    display: flex;
    flex-direction: column;
    gap: 2px;
    margin-top: 8px;
  }

  .row {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 4px;
    border-radius: 6px;
    cursor: default;
  }
  .row.clickable {
    cursor: pointer;
  }
  .row.clickable:hover {
    background: var(--secondary-background-color, #f5f5f5);
  }

  .row-main {
    flex: 1 1 auto;
    min-width: 0;
  }
  .row-name {
    font-size: 14px;
    color: var(--primary-text-color);
    font-weight: 500;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  .row-location {
    font-size: 12px;
    color: var(--secondary-text-color);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .owner-pill {
    flex: 0 0 auto;
    padding: 2px 8px;
    font-size: 11px;
    border-radius: 999px;
    background: var(--primary-color, #03a9f4);
    color: var(--text-primary-color, #fff);
    white-space: nowrap;
  }

  .smart-matches-header {
    margin-top: 12px;
    padding: 4px 4px 6px;
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--secondary-text-color);
    border-top: 1px solid var(--divider-color, #e0e0e0);
  }

  .semantic-loading {
    padding: 4px 4px;
    font-size: 12px;
    color: var(--secondary-text-color);
    font-style: italic;
  }
`,vt=10,bt=10,wt=400;console.info("%c STORAGEHUB-CARD %c v2.0.0 ","color: white; background: #03a9f4; font-weight: 700","color: #03a9f4; background: white; font-weight: 700"),window.customCards=window.customCards||[],window.customCards.push({type:"storagehub-card",name:"StorageHub Search",description:"Search your StorageHub inventory with instant local matches and a semantic fallback."});let At=class extends ot{constructor(){super(...arguments),this._query="",this._localResults=[],this._semanticResults=[],this._loadingIndex=!0,this._loadingSemantic=!1,this._error=null,this._semanticError=null,this._index=null,this._debounceHandle=null,this._unsubEtag=null,this._semanticGen=0}static{this.styles=yt}setConfig(t){if(!t||"custom:storagehub-card"!==t.type)throw new Error("Invalid configuration: type must be custom:storagehub-card");const e=t.max_local_results??vt,s=t.max_semantic_results??bt,i=t.semantic_debounce_ms??wt;if(e<1||e>100)throw new Error("max_local_results must be 1–100");if(s<1||s>50)throw new Error("max_semantic_results must be 1–50");if(i<0||i>5e3)throw new Error("semantic_debounce_ms must be 0–5000");this._config={type:"custom:storagehub-card",storagehub_url:t.storagehub_url,max_local_results:e,max_semantic_results:s,semantic_debounce_ms:i}}static getStubConfig(){return{type:"custom:storagehub-card"}}getCardSize(){return 4}connectedCallback(){super.connectedCallback(),this._loadIndex(),this._subscribeUpdates()}disconnectedCallback(){super.disconnectedCallback(),null!==this._debounceHandle&&(window.clearTimeout(this._debounceHandle),this._debounceHandle=null),this._unsubEtag?.(),this._unsubEtag=null}async _loadIndex(){if(this.hass){this._loadingIndex=!0,this._error=null;try{const t=await async function(t){return(await t.callService("storagehub","search_lite",{},void 0,!1,!0)).response}(this.hass);this._index=new gt(t.items),this._query&&this._recomputeLocal()}catch(t){this._error=`Could not load inventory index: ${t.message??t}`}finally{this._loadingIndex=!1}}}async _subscribeUpdates(){if(this.hass&&!this._unsubEtag)try{this._unsubEtag=await async function(t,e,s){return t.connection.subscribeEvents(t=>{t.data.entity_id===e&&s()},"state_changed")}(this.hass,"sensor.storagehub_index_etag",()=>{this._loadIndex()})}catch{}}_onInput(t){const e=t.target.value;this._query=e,this._recomputeLocal(),this._scheduleSemantic()}_onKeydown(t){"Enter"===t.key&&(null!==this._debounceHandle&&(window.clearTimeout(this._debounceHandle),this._debounceHandle=null),this._runSemantic())}_recomputeLocal(){!this._index||this._query.trim().length<2?this._localResults=[]:this._localResults=this._index.search(this._query,this._config.max_local_results)}_scheduleSemantic(){if(null!==this._debounceHandle&&window.clearTimeout(this._debounceHandle),this._query.trim().length<2)return this._semanticResults=[],this._semanticError=null,void(this._debounceHandle=null);this._debounceHandle=window.setTimeout(()=>{this._debounceHandle=null,this._runSemantic()},this._config.semantic_debounce_ms)}async _runSemantic(){if(!this.hass||this._query.trim().length<2)return;const t=++this._semanticGen;this._loadingSemantic=!0,this._semanticError=null;try{const e=await async function(t,e,s){return(await t.callService("storagehub","semantic_search",{query:e,limit:s},void 0,!1,!0)).response}(this.hass,this._query,this._config.max_semantic_results);if(t!==this._semanticGen)return;const s=new Set(this._localResults.map(t=>t.entry.id));this._semanticResults=e.items.filter(t=>!s.has(t.id))}catch(e){if(t!==this._semanticGen)return;this._semanticError=`Smart search unavailable: ${e.message??e}`,this._semanticResults=[]}finally{t===this._semanticGen&&(this._loadingSemantic=!1)}}_openItem(t){if(!this._config.storagehub_url)return;const e=this._config.storagehub_url.replace(/\/+$/,"");window.open(`${e}/items/${t}`,"_blank","noopener")}_renderRow(t,e,s,i,n){const r=[s?`${s}`:null,i?`in ${i}`:null].filter(t=>null!==t).join(" "),o=!!this._config.storagehub_url;return D`
      <div
        class="row ${o?"clickable":""}"
        @click=${o?()=>this._openItem(t):void 0}
      >
        <div class="row-main">
          <div class="row-name">${e}</div>
          <div class="row-location">${r||"—"}</div>
        </div>
        ${n?D`<span class="owner-pill">${n}</span>`:W}
      </div>
    `}render(){const t=!this._loadingIndex&&!this._error&&0===this._index?.size,e=this._query.trim().length>=2;return D`
      <ha-card>
        <input
          class="search-input"
          type="text"
          placeholder="Search inventory…"
          .value=${this._query}
          @input=${this._onInput}
          @keydown=${this._onKeydown}
          autocomplete="off"
          spellcheck="false"
        />
        ${this._error?D`<div class="error">${this._error}</div>`:W}
        ${this._loadingIndex?D`<div class="loading">Loading inventory…</div>`:W}
        ${t?D`<div class="empty">No items in inventory yet.</div>`:W}
        ${e&&0===this._localResults.length&&!this._loadingSemantic&&0===this._semanticResults.length?D`<div class="empty">No matches.</div>`:W}
        <div class="results">
          ${this._localResults.map(t=>this._renderRow(t.entry.id,t.entry.name,t.entry.container_name,t.entry.location_name,t.entry.owner_name))}
        </div>
        ${this._semanticError?D`<div class="error">${this._semanticError}</div>`:W}
        ${this._semanticResults.length>0?D`<div class="smart-matches-header">Smart matches</div>
              <div class="results">
                ${this._semanticResults.map(t=>this._renderRow(t.id,t.name,t.container_name,t.location_name,t.owner_name))}
              </div>`:W}
        ${this._loadingSemantic&&0===this._semanticResults.length?D`<div class="semantic-loading">Looking deeper…</div>`:W}
      </ha-card>
    `}};t([ht({attribute:!1})],At.prototype,"hass",void 0),t([dt()],At.prototype,"_query",void 0),t([dt()],At.prototype,"_localResults",void 0),t([dt()],At.prototype,"_semanticResults",void 0),t([dt()],At.prototype,"_loadingIndex",void 0),t([dt()],At.prototype,"_loadingSemantic",void 0),t([dt()],At.prototype,"_error",void 0),t([dt()],At.prototype,"_semanticError",void 0),At=t([(t=>(e,s)=>{void 0!==s?s.addInitializer(()=>{customElements.define(t,e)}):customElements.define(t,e)})("storagehub-card")],At);export{At as StorageHubCard};
