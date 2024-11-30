import { SVGProps } from 'react'

interface UploadProps extends SVGProps<SVGSVGElement> {
  strokeColor?: string
}

export const Upload = ({ ...props }: UploadProps) => (
  <svg
    width="36"
    height="35"
    viewBox="0 0 36 35"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    {...props}
  >
    <g clip-path="url(#clip0_58_878)">
      <path
        d="M27.3337 10.7606C27.0699 10.6853 26.8292 10.5453 26.6333 10.3532C26.4374 10.1612 26.2927 9.92322 26.2123 9.66097C25.7657 8.14729 25.0166 6.73994 24.0104 5.52411C23.0043 4.30827 21.7618 3.30922 20.3584 2.58741C18.9549 1.8656 17.4196 1.43604 15.8454 1.32472C14.2711 1.21339 12.6906 1.42263 11.1996 1.93976C9.70853 2.45689 8.33789 3.27116 7.17061 4.33331C6.00334 5.39545 5.0637 6.68338 4.40854 8.11915C3.75339 9.55493 3.39636 11.1087 3.35904 12.6865C3.32172 14.2642 3.6049 15.8331 4.19143 17.2983C4.32618 17.6066 4.35519 17.9508 4.27395 18.2774C4.19271 18.6039 4.00578 18.8944 3.74227 19.1037C2.58104 19.9655 1.67442 21.1253 1.11836 22.4603C0.562308 23.7952 0.377507 25.2556 0.583517 26.687C0.905011 28.622 1.90961 30.3777 3.41499 31.6353C4.92037 32.8929 6.82674 33.5691 8.7881 33.5412H16.5421C16.9288 33.5412 17.2998 33.3875 17.5733 33.114C17.8467 32.8406 18.0004 32.4696 18.0004 32.0828C18.0004 31.6961 17.8467 31.3251 17.5733 31.0516C17.2998 30.7782 16.9288 30.6245 16.5421 30.6245H8.7881C7.52851 30.6551 6.29964 30.2334 5.32421 29.4359C4.34878 28.6384 3.69133 27.5178 3.47102 26.2772C3.33131 25.3654 3.44454 24.4327 3.79837 23.5807C4.15221 22.7288 4.73308 21.9903 5.47768 21.4458C6.25982 20.8612 6.8256 20.0334 7.08613 19.0923C7.34667 18.1513 7.2872 17.1504 6.91706 16.2468C6.1852 14.3141 6.14757 12.1871 6.8106 10.2297C7.34026 8.69639 8.28875 7.34204 9.5486 6.32009C10.8085 5.29813 12.3293 4.64941 13.9389 4.44743C14.3123 4.39936 14.6883 4.37501 15.0648 4.37451C16.9505 4.36829 18.7875 4.97306 20.3007 6.09825C21.8139 7.22344 22.922 8.80853 23.4589 10.6162C23.6685 11.3051 24.0462 11.931 24.5579 12.4376C25.0696 12.9442 25.6993 13.3156 26.3902 13.5183C28.0811 14.0184 29.5789 15.0231 30.6831 16.3979C31.7872 17.7728 32.4451 19.4521 32.5685 21.2111C32.6919 22.9701 32.275 24.7248 31.3736 26.2404C30.4722 27.7559 29.1293 28.9599 27.5248 29.6912C27.2873 29.8128 27.0888 29.9987 26.9519 30.2276C26.8149 30.4566 26.7451 30.7194 26.7504 30.9862V30.9862C26.7476 31.2275 26.8054 31.4657 26.9185 31.6788C27.0317 31.892 27.1966 32.0733 27.3981 32.2061C27.5996 32.3389 27.8312 32.419 28.0717 32.439C28.3122 32.459 28.5539 32.4183 28.7746 32.3206C34.8033 29.4228 38.0787 21.8001 32.9746 14.4356C31.5692 12.6023 29.5785 11.3054 27.3337 10.7606V10.7606Z"
        fill="#373645"
      />
      <path
        d="M27.781 24.3642C28.0544 24.0907 28.208 23.7198 28.208 23.3332C28.208 22.9465 28.0544 22.5756 27.781 22.3021L25.4681 19.9892C24.6477 19.169 23.5351 18.7083 22.375 18.7083C21.2149 18.7083 20.1023 19.169 19.2819 19.9892L16.9689 22.3021C16.7033 22.5772 16.5563 22.9455 16.5596 23.3279C16.5629 23.7103 16.7163 24.076 16.9867 24.3464C17.2571 24.6168 17.6229 24.7702 18.0052 24.7735C18.3876 24.7768 18.756 24.6298 19.031 24.3642L20.9167 22.4786V33.5415C20.9167 33.9283 21.0703 34.2992 21.3438 34.5727C21.6173 34.8462 21.9882 34.9998 22.375 34.9998C22.7618 34.9998 23.1327 34.8462 23.4062 34.5727C23.6797 34.2992 23.8333 33.9283 23.8333 33.5415V22.4786L25.7189 24.3642C25.9924 24.6376 26.3633 24.7912 26.75 24.7912C27.1367 24.7912 27.5076 24.6376 27.781 24.3642Z"
        fill="#373645"
      />
    </g>
    <defs>
      <clipPath id="clip0_58_878">
        <rect width="35" height="35" fill="white" transform="translate(0.5)" />
      </clipPath>
    </defs>
  </svg>
)
